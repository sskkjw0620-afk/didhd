import React, { useState, useRef, useEffect } from 'react'
import Thumbnail from './Thumbnail'

export default function SlideViewer({ slides }) {
  const [index, setIndex] = useState(0)
  const [analysis, setAnalysis] = useState(null)
  const audioRef = useRef(null)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)

  useEffect(() => {
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])

  const goTo = (i) => setIndex(Math.max(0, Math.min(i, slides.length - 1)))

  const onUpload = async (e) => {
    const file = e.target.files && e.target.files[0]
    if (!file) return
    const url = URL.createObjectURL(file)
    setAnalysis({ name: file.name, duration: null, label: '분석 중...' })

    // set audio src and try to load metadata
    if (audioRef.current) {
      audioRef.current.src = url
      try {
        await audioRef.current.play().catch(() => {})
      } catch {}
    }

    // setup audio context and analyser (client-side quick analysis)
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext
      if (!audioContextRef.current) audioContextRef.current = new AudioContext()
      const ac = audioContextRef.current

      // create analyser and connect
      if (analyserRef.current) analyserRef.current.disconnect()
      const analyser = ac.createAnalyser()
      analyser.fftSize = 2048
      analyserRef.current = analyser

      const source = ac.createMediaElementSource(audioRef.current)
      source.connect(analyser)
      analyser.connect(ac.destination)

      // wait briefly for audio to produce data
      setTimeout(() => {
        const bufferLength = analyser.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)
        analyser.getByteFrequencyData(dataArray)
        // find peak
        let max = -Infinity
        let maxIndex = 0
        for (let i = 0; i < dataArray.length; i++) {
          if (dataArray[i] > max) {
            max = dataArray[i]
            maxIndex = i
          }
        }
        const sampleRate = ac.sampleRate
        const dominantFreq = maxIndex * (sampleRate / analyser.fftSize)
        const duration = Math.round(audioRef.current.duration || 0)

        // simple heuristic classifier
        let label = '중립'
        if (dominantFreq > 1000) label = '높은 음 — 긍정/관심 요청 가능성'
        else if (dominantFreq > 300) label = '중간 음 — 일반적 요청'
        else label = '낮은 음 — 경고/불만 가능성'

        setAnalysis({ name: file.name, duration, label, dominantFreq: Math.round(dominantFreq) })
      }, 400)
    } catch (err) {
      setAnalysis({ name: file.name, duration: null, label: '분석 불가' })
    }

    // also send to server for a more robust analysis if available
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch('/api/analyze', { method: 'POST', body: form })
      if (res.ok) {
        const data = await res.json()
        setAnalysis(prev => ({ ...(prev || {}), server: data }))
      } else {
        // ignore server error
      }
    } catch (e) {
      // server not available locally
    }
  }

  if (!slides || slides.length === 0) {
    return <div>슬라이드가 없습니다. 먼저 `extract_pptx.py`로 `slides.json`을 생성하세요.</div>
  }

  const s = slides[index]

  return (
    <div>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: 6 }}>
          <button onClick={() => goTo(index - 1)}>&lt; 이전</button>
          <button onClick={() => goTo(index + 1)}>다음 &gt;</button>
        </div>

        <div style={{ marginLeft: 12, display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 6 }}>
          {slides.map((sl, i) => (
            <Thumbnail key={i} slide={sl} active={i === index} onClick={() => goTo(i)} />
          ))}
        </div>

        <div style={{ marginLeft: 'auto' }}>
          <label style={{ marginRight: 8 }}>오디오 업로드:</label>
          <input type="file" accept="audio/*" onChange={onUpload} />
        </div>
      </div>

      <h2>슬라이드 {s.index}</h2>
      <div style={{ border: '1px solid #ddd', padding: 12, borderRadius: 6 }}>
        {s.texts && s.texts.map((t, i) => (
          <p key={i} style={{ margin: 6 }}>{t}</p>
        ))}

        {s.images && s.images.map((img, i) => (
          <img key={i} src={img} alt={`slide-${s.index}-img-${i}`} style={{ maxWidth: '100%', marginTop: 8 }} />
        ))}
      </div>

      <div style={{ marginTop: 12 }}>
        <h3>업로드된 오디오 해석</h3>
        <audio ref={audioRef} controls style={{ width: '100%' }} />
        {analysis ? (
          <div style={{ marginTop: 8 }}>
            <div>- 파일명: {analysis.name}</div>
            <div>- 재생시간(초): {analysis.duration ?? (analysis.server && analysis.server.duration) ?? '알 수 없음'}</div>
            <div>- 우세 주파수(Hz): {analysis.dominantFreq ?? (analysis.server && analysis.server.dominant_freq) ?? '측정불가'}</div>
            <div>- 해석(클라이언트): {analysis.label}</div>
            {analysis.server && (
              <div style={{ marginTop: 6 }}>
                <div>- 서버 해석: {analysis.server.label} (긴급도: {analysis.server.urgency})</div>
                <div style={{ color: '#666' }}>- 서버 기반 분석은 librosa 특성으로 계산됩니다.</div>
              </div>
            )}
            <div style={{ marginTop: 6, color: '#666' }}>- 주의: 자동 분류는 휴리스틱입니다. 정밀 분석은 모델 연동이 필요합니다.</div>
          </div>
        ) : (
          <div style={{ marginTop: 8 }}>오디오를 업로드하면 간단한 주파수 분석을 실행합니다.</div>
        )}
      </div>
    </div>
  )
}
