import { Trade } from './trade';
import { Position } from './position';
import { Pnl } from './pnl';

export interface TradeFeedback {
  trade: Trade;
  position: Position;
  pnl: Pnl[];
}
