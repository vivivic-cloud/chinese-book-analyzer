#!/usr/bin/env swift
// Vision framework OCR — language-aware text extraction
import Vision
import AppKit
import Foundation

let args = CommandLine.arguments
guard args.count >= 2 else {
    fputs("usage: swift ocr.swift <image_path> [lang...]\n", stderr)
    exit(1)
}

let imagePath = args[1]

// 언어 목록: 인자로 받거나 기본값 (CJK + 영어 전부 시도)
let langs: [String] = args.count > 2
    ? Array(args[2...])
    : ["zh-Hans", "zh-Hant", "ja-JP", "ko-KR", "en-US"]

guard let image = NSImage(contentsOfFile: imagePath),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    fputs("이미지 로드 실패: \(imagePath)\n", stderr)
    exit(1)
}

let semaphore = DispatchSemaphore(value: 0)
var lines: [String] = []

let request = VNRecognizeTextRequest { req, err in
    defer { semaphore.signal() }
    if let e = err { fputs("Vision 오류: \(e)\n", stderr); return }
    guard let observations = req.results as? [VNRecognizedTextObservation] else { return }
    // 위→아래 순서 (bounding box y 내림차순)
    let sorted = observations.sorted { $0.boundingBox.minY > $1.boundingBox.minY }
    lines = sorted.compactMap { $0.topCandidates(1).first?.string }
}

request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
request.recognitionLanguages = langs
// 자동 언어 감지 활성화
if #available(macOS 13, *) {
    request.automaticallyDetectsLanguage = true
}

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
    semaphore.wait()
    print(lines.joined(separator: "\n"))
} catch {
    fputs("OCR 실패: \(error)\n", stderr)
    exit(1)
}
