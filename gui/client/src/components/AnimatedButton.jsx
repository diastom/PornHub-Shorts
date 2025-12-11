import React from 'react';
import { motion } from 'framer-motion';
import './AnimatedButton.css';

const AnimatedButton = ({ children, onClick, variant = 'primary', className = '' }) => {
  return (
    <motion.button
      className={`animated-btn ${variant} ${className}`}
      onClick={onClick}
      whileHover={{ scale: 1.05, boxShadow: "0px 0px 15px var(--accent-glow)" }}
      whileTap={{ scale: 0.95 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
    >
      {children}
    </motion.button>
  );
};

export default AnimatedButton;
