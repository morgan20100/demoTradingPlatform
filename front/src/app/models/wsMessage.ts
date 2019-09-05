export interface WSMessage {
  data: {
    type: string;
    content: any;
  };
}
