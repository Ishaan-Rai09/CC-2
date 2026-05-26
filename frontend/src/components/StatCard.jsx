import { motion } from 'framer-motion';

const StatCard = ({ title, value }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm"
    >
      <h3 className="text-sm font-medium text-[var(--color-text-secondary)] mb-2">{title}</h3>
      <p className="text-3xl font-bold text-[var(--color-text-primary)]">{value}</p>
    </motion.div>
  );
};

export default StatCard;
