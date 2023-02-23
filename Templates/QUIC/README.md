# nscap_hw5

## Problem

With QUIC's header and frame structure, implement following function on UDP socket.

- Error Control
- Flow Control
- Congestion Control

## Test

Build a pair of client and server to send message to each others. Use slides and screenshot to prove you have implemented the above functions and using QUIC header and frame structure.

## TIPs

* 在QUIC裡有很多變動長度的欄位，全部指定為固定長度欄位即可
* 可稍微簡化交握流程，本次作業重點在於Error Control, Flow Control和Congestion Control的實作
* Error Control測試可以隨機讓部分封包遺失，並查看是否有重送
* Flow Control可以讓其中一方在處理封包時`time.sleep(0.5)`等
* Congestion Control測試可以隨機讓部分封包遺失，並查看Congestion Window大小
* `struct.pack, struct.unpack`可用於將資料以指定型別轉換成`bytes`
* 也可以使用`ctypes.BigEndianStructure`來代替`struct`
* `int.to_bytes, int.from_bytes`可將`int`型別轉換成指定長度的`bytes`及反向
* 善用`threading`及`heapq`