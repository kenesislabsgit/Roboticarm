export interface Camera {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'alert';
  region: string;
}

export interface Incident {
  id: string;
  cameraId: string;
  cameraName: string;
  type: string;
  timestamp: string;
  evidenceUrl: string;
  severity: 'low' | 'medium' | 'high';
}
