import React from 'react';

const StatusBadge = ({ status }) => (
  <span className={`status-badge ${status.toLowerCase()}`}>
    {status}
  </span>
);

export default StatusBadge;