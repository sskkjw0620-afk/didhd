import React, { useEffect, useState } from 'react'
import SlideViewer from './components/SlideViewer'

export default function App() {
  const [slides, setSlides] = useState([])

  useEffect(() => {
    fetch('/slides.json')
      .then(res => res.json())
      .then(data => setSlides(data))
      .catch(() => setSlides([]))
  }, [])

  return (
    <div style={{ padding: 20, fontFamily: 'Arial, sans-serif' }}>
      <h1>고양이 울음소리 해석 — 슬라이드 뷰어</h1>
      <p>왼쪽/오른쪽 버튼으로 슬라이드를 이동하세요. 오디오 업로드 후 간단 해석 표시.</p>
      <SlideViewer slides={slides} />
    </div>
  )
}
