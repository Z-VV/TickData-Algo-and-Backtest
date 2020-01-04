New project that I have worked lately.

Trading algorithm,that uses FIX (Financial Information Exchange) API(up to 200 price changes per second),
which is much faster and reliable than REST API.
The idea is to catch rapid grow in the volume of the trades and price changes,suggests continuation of the move for the next 1-3 minutes.
C++ program is working in the background,receiving high-speed price-data stream and saving the ticks in the log.file .
FURY2.py is reading the messages in the file and extracting the valuable price ticks every second.

FuryBacktest.py  is downloading and preparing the tick data from the past then checking if the algorithm is profitable.
