export interface Clock {
  now(): number;
}

export class RealClock implements Clock {
  public now(): number {
    return Date.now();
  }
}

export class FakeClock implements Clock {
  private currentMs: number;

  public constructor(initialMs = 0) {
    this.currentMs = initialMs;
  }

  public now(): number {
    return this.currentMs;
  }

  public set(ms: number): void {
    this.currentMs = Math.max(0, Math.floor(ms));
  }

  public advance(deltaMs: number): void {
    this.currentMs = Math.max(0, this.currentMs + Math.floor(deltaMs));
  }
}
