CON

  'Set up the clock mode
  _clkmode = xtal1 + pll16x
  _xinfreq = 5_000_000
  '5 MHz clock * 16x PLL = 80 MHz system clock speed
  
OBJ
  module:        "xfi_serial"
  create:       "FullDuplexSerialAdv"

VAR
  byte tmpMessage[254]
  long moduleIP
  word modulePort

PUB Main | bytein,len,slot

  dira[16..23]~~
  create.Start(31, 30, %0000, 57_600)
  waitcnt(cnt + (1 * clkfreq))
  module.Start(27,26)
  outa[16]~~
  create.Tx(128)
  create.Tx(132)

  repeat

    if not module.RxEmpty
      bytefill(@tmpMessage,0,254)
      len.byte[3] := module.Length
      module.Read(@tmpMessage)
      ParseFrameData(@tmpMessage,len.byte[3])
      

    'if (bytein := create.RxCheck) => 0
    '  if not module.TxFull
    '    bytefill(@tmpMessage,0,254)
    '    len := 1
    '    byte[@tmpMessage] := bytein
    '    repeat until (bytein := create.Rx) == 10
    '      byte[@tmpMessage][len] := bytein
    '      len += 1
    '    create.Tx(module.Write(len,@tmpMessage))
    '    create.Tx($0D)
    '  else
    '    create.Str(STRING("> Queue is full"))
    '    create.Tx($0D)

PUB ParseFrameData(data,len)|senderIP,senderPort,protocol

  case byte[data]
    $B0:  senderIP.byte[0] := byte[data][1]
          senderIP.byte[1] := byte[data][2]
          senderIP.byte[2] := byte[data][3]
          senderIP.byte[3] := byte[data][4]
          senderPort.byte[2] := byte[data][7]
          senderPort.byte[3] := byte[data][8]
          protocol.byte[3] := byte[data][9]
          ParseCreateCommand(data + 11,len - 11)

PUB ParseCreateCommand(data,len)|byteNum

  if byte[data] == 127
    repeat byteNum from 1 to len-1
      create.Tx(byte[data][byteNum])

PUB SensorPacketLength(packetId)

  if packetId < 7
    return lookupz(packetId,groupPackets)
  elseif packetId > 42
    return 0
  else
    if lookdown(packetId,doublePackets) > 0
      return 2
    else
      return 1  

DAT
        doublePackets byte 19,20,22,23,25,26,27,28,29,30,31,33,39,40,41,42
        groupPackets byte 26,10,6,10,14,12,52                   