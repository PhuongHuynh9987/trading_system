    
                        │  Simple Dashboad      │
                        │ (Market + News)       │
                        └─--┬──────--─----┬-----┘
                            │             |
                            ▼             ▼
                                            


                                    ┌───────────────┐
                                    |    Get data   |
                                    |   from Apaca  |
                                    └──────-┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ Feature Eng.  │
                                    │ (Signals)     │
                                    └──────-┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ ML Model      │
                                    │ (Prediction)  │
                                    └──────-┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ Strategy      │
                                    │ (BUY/SELL)    │
                                    └──────-┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ Execution     │
                                    │ (Broker API)  │
                                    └──────-┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ Monitoring UI │
                                    │ (Dashboard)   │
                                    └───────────────┘