export default class WSConnection {
  private listeners: Record<string, ((evt: object) => void)[]> = {};

  constructor(private readonly ws: WebSocket) {
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      const listeners = this.listeners[msg.type];
      for (let listener of listeners) {
        listener(msg);
      }
    };
  }

  public addEventListener(type: string, listener: (evt: object) => void) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(listener);
  }

  public removeEventListener(type: string, listener: (evt: object) => void) {
    const listeners = this.listeners[type];
    if (listeners) {
      const i = listeners.indexOf(listener);
      if (i !== -1) {
        listeners.splice(i, 1);
      }
    }
  }
}
