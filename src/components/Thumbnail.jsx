import React from 'react'

export default function Thumbnail({ slide, active, onClick }) {
  const excerpt = slide.texts && slide.texts.length > 0 ? slide.texts[0].slice(0, 60) : `Slide ${slide.index}`
  const img = slide.images && slide.images.length > 0 ? slide.images[0] : null

  return (
    <div onClick={onClick} style={{ cursor: 'pointer', border: active ? '2px solid #2b7cff' : '1px solid #ddd', padding: 8, borderRadius: 6, width: 140 }}>
      <div style={{ height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff' }}>
        {img ? (
          <img src={img} alt={`thumb-${slide.index}`} style={{ maxWidth: '100%', maxHeight: '100%' }} />
        ) : (
          <div style={{ padding: 6, color: '#444', fontSize: 12 }}>{excerpt}</div>
        )}
      </div>
      <div style={{ marginTop: 8, textAlign: 'center', fontSize: 13 }}>{`슬라이드 ${slide.index}`}</div>
    </div>
  )
}
