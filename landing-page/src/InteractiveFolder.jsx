import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * GrungeInteractiveFolder Component v4 - CLIPPING FIX
 * Elements are structurally separated to prevent deckle-edge clipping of labels.
 */

const darkenColor = (hex, percent) => {
  let color = hex.startsWith('#') ? hex.slice(1) : hex;
  if (color.length === 3) {
    color = color.split('').map(c => c + c).join('');
  }
  const num = parseInt(color, 16);
  let r = (num >> 16) & 0xff;
  let g = (num >> 8) & 0xff;
  let b = num & 0xff;
  r = Math.max(0, Math.min(255, Math.floor(r * (1 - percent))));
  g = Math.max(0, Math.min(255, Math.floor(g * (1 - percent))));
  b = Math.max(0, Math.min(255, Math.floor(b * (1 - percent))));
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
};

export function InteractiveFolder({ 
  color = '#DC143C', 
  size = 1, 
  items = [], 
  className = '',
  label,
  onOpenVault
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const maxVisibleItems = 3;
  const displayItems = items.slice(0, maxVisibleItems);
  while (displayItems.length < maxVisibleItems) {
    displayItems.push(null);
  }

  const folderBackColor = darkenColor(color, 0.3);
  const paperColor = '#F2EBE0'; 

  const handleMouseMove = (e, index) => {
    if (!isOpen) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - (rect.left + rect.width / 2)) * 0.6;
    const y = (e.clientY - (rect.top + rect.height / 2)) * 0.6;
    setMousePos({ x, y });
    setHoveredIndex(index);
  };

  const handleMouseLeave = () => {
    setMousePos({ x: 0, y: 0 });
    setHoveredIndex(null);
  };

  const getPaperTransform = (index) => {
    if (!isOpen) return { x: '-50%', y: '25%', rotate: (index - 1) * 6, scale: 0.9 };
    
    const baseTransforms = [
      { x: '-145%', y: '-120%', rotate: -25 },
      { x: '35%', y: '-120%', rotate: 25 },
      { x: '-50%', y: '-170%', rotate: 0 }
    ];

    const base = baseTransforms[index] || { x: '-50%', y: '-50%', rotate: 0 };
    
    if (hoveredIndex === index) {
      return {
        x: `calc(${base.x} + ${mousePos.x}px)`,
        y: `calc(${base.y} + ${mousePos.y}px)`,
        rotate: base.rotate,
        scale: 1.35,
      };
    }
    
    return base;
  };

  const flapCommonStyle = {
    position: 'absolute',
    inset: -4,
    zIndex: 30,
    transformOrigin: 'bottom',
    backgroundColor: color,
    border: '6px solid var(--color-black)',
    backgroundImage: 'url("https://www.transparenttextures.com/patterns/carbon-fibre.png"), linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.5))',
    backgroundBlendMode: 'overlay',
    boxShadow: 'inset 0 0 50px rgba(0,0,0,0.4)'
  };

  return (
    <div 
      className={`jitter-el ${className}`}
      style={{ 
        transform: `scale(${size})`, 
        padding: '80px', // Extra padding for papers
        width: 180, 
        height: 140, 
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      <div
        style={{ cursor: 'pointer', position: 'relative', userSelect: 'none', width: '160px', height: '120px' }}
        onClick={() => {
            setIsOpen(!isOpen);
            if (isOpen && onOpenVault) onOpenVault();
        }}
      >
        {/* PHYSICAL BACKING PIECE */}
        <div
          style={{ 
            position: 'absolute',
            inset: 0,
            backgroundColor: folderBackColor,
            borderRadius: '4px 16px 16px 16px',
            border: '6px solid var(--color-black)',
            boxShadow: isOpen ? '0 0 100px rgba(220, 20, 60, 0.5)' : '25px 25px 0 var(--color-black)',
            backgroundImage: 'url("https://www.transparenttextures.com/patterns/micro-fab.png")',
            clipPath: 'polygon(0% 0%, 100% 0%, 100% 85%, 85% 100%, 0% 100%)' 
          }}
        />

        {/* TOP TAB (Separate to avoid clipping base) */}
        <div
            style={{ 
                position: 'absolute', 
                bottom: '100%', 
                left: -6, 
                width: '70px', 
                height: '28px', 
                backgroundColor: folderBackColor,
                border: '6px solid var(--color-black)',
                borderBottom: 'none',
                borderRadius: '14px 14px 0 0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '11px',
                color: 'white',
                fontFamily: 'var(--font-mono)',
                fontWeight: 900,
                letterSpacing: '1px',
                zIndex: 10
            }}
        >
            ARCHIVE
        </div>

        {/* PAPERS (Deepest) */}
        {displayItems.map((item, i) => (
            <motion.div
                key={i}
                onMouseMove={(e) => handleMouseMove(e, i)}
                onMouseLeave={handleMouseLeave}
                animate={getPaperTransform(i)}
                transition={{ type: 'spring', stiffness: 350, damping: 22 }}
                style={{
                    position: 'absolute',
                    left: '50%',
                    zIndex: 20,
                    backgroundColor: paperColor,
                    border: '4px solid var(--color-black)',
                    width: i === 0 ? '110px' : i === 1 ? '120px' : '130px',
                    height: i === 0 ? '90px' : i === 1 ? '100px' : '110px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '12px',
                    backgroundImage: 'url("https://www.transparenttextures.com/patterns/paper-fibers.png")',
                    boxShadow: '15px 15px 0 rgba(0,0,0,0.2)',
                    borderRadius: '2px'
                }}
            >
                <div style={{ color: 'var(--color-crimson)', filter: 'drop-shadow(4px 4px 0 rgba(0,0,0,0.2))' }}>
                    {item || (
                        <div style={{ opacity: 0.1, width: '100%' }}>
                            <div style={{ height: 10, background: 'black', marginBottom: 10 }} />
                            <div style={{ height: 10, background: 'black', width: '80%', marginBottom: 10 }} />
                            <div style={{ height: 10, background: 'black', width: '50%' }} />
                        </div>
                    )}
                </div>
            </motion.div>
        ))}

        {/* CLIPPED FLAPS */}
        <div style={{ position: 'absolute', inset: 0, zIndex: 30, pointerEvents: 'none' }}>
            <motion.div
                animate={{ skewX: isOpen ? 35 : 0, scaleY: isOpen ? 0.25 : 1, translateY: isOpen ? 40 : 0 }}
                transition={{ type: 'spring', stiffness: 400, damping: 28 }}
                style={{ ...flapCommonStyle, clipPath: 'polygon(0 0, 50% 0, 50% 100%, 0 100%)' }}
            />
            <motion.div
                animate={{ skewX: isOpen ? -35 : 0, scaleY: isOpen ? 0.25 : 1, translateY: isOpen ? 40 : 0 }}
                transition={{ type: 'spring', stiffness: 400, damping: 28 }}
                style={{ ...flapCommonStyle, clipPath: 'polygon(50% 0, 100% 0, 100% 100%, 50% 100%)' }}
            />
        </div>

        {/* LABEL OVERLAY (SAFE FROM CLIPPING) */}
        <motion.div
            animate={{ opacity: isOpen ? 0 : 1, scale: isOpen ? 0.7 : 1, y: isOpen ? 30 : 0 }}
            style={{
                position: 'absolute',
                inset: -60, // Large area to prevent clamping
                zIndex: 40,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                pointerEvents: 'none'
            }}
        >
             {label && (
              <div style={{
                color: 'white',
                fontFamily: 'var(--font-hero)',
                fontSize: '20px',
                fontWeight: 900,
                textTransform: 'uppercase',
                background: 'var(--color-black)',
                padding: '8px 18px',
                whiteSpace: 'nowrap',
                boxShadow: '10px 10px 0 var(--color-crimson)',
                border: '4px solid white',
                transform: 'rotate(-3deg)'
              }}>
                {label}
              </div>
            )}
        </motion.div>

        {/* ACCESS BANNER */}
        <AnimatePresence>
            {isOpen && (
              <motion.div
                initial={{ opacity: 0, y: -40, scale: 0.8 }}
                animate={{ opacity: 1, y: 70, scale: 1 }}
                exit={{ opacity: 0, y: -40, scale: 0.8 }}
                style={{
                    position: 'absolute',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    zIndex: 50,
                    width: 'max-content'
                }}
              >
                  <div style={{
                      background: 'var(--color-black)',
                      border: '5px solid var(--color-crimson)',
                      color: 'white',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '16px',
                      fontWeight: 900,
                      padding: '10px 20px',
                      boxShadow: '20px 20px 0 rgba(220, 20, 60, 0.4)',
                      letterSpacing: '3px'
                  }}>
                     [ OVERRIDE_ACCESS_GRANTED ]
                  </div>
              </motion.div>
            )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default InteractiveFolder;
