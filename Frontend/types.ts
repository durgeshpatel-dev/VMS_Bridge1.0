export interface User {
  name: string;
  email: string;
  avatar: string;
  role: string;
}

export enum Severity {
  CRITICAL = 'Critical',
  HIGH = 'High',
  MEDIUM = 'Medium',
  LOW = 'Low',
  INFO = 'Info'
}

export interface Vulnerability {
  id: string;
  name: string;
  cve?: string;
  severity: Severity;
  asset: string;
  discoveredAt: string;
  aiScore: number;
  status: 'Open' | 'In Progress' | 'Fixed';
  description?: string;
  remediation?: string;
  jiraKey?: string;
}

export interface StatMetric {
  label: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: string;
  color: string;
}

export interface UploadedScan {
  id: string;
  filename: string;
  team: 'SEC' | 'IT' | 'PROD';
  size: string;
  date: string;
  status: 'RUNNING' | 'PROCESSED' | 'FAILED';
}

export interface Job {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number | null;
  job_type: string;
}