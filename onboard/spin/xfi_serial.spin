OBJ

  module        :"FullDuplexSerialAdv"
  instack       :"Message_Queue"
  outstack      :"Message_Queue"

VAR

  byte  inarr[4096]
  byte  outarr[4096]
  byte  tmparr[254]
  long  stack[24]

PUB Start(rxPin,txPin)

  module.Start(rxPin,txPin,%0000,57_600)
  waitcnt(cnt + (1 * clkfreq))
  instack.init(@inarr,4096,256)
  outstack.init(@outarr,4096,256)
  cognew(Listener, @stack) 

PUB Stop

  module.Stop

PUB Write(len, data)

  return outstack.write(len, data)

PUB Read(output_addr)

  return instack.read(output_addr)

PUB TxFull

  return outstack.full

PUB RxEmpty

  return instack.empty

PUB Length

  return instack.length

PUB PullFrame|len,sum,bytenum,tmp

  if not instack.full
    if module.RxCheck == 126

      len := 0
                                                 
      len.byte[2] := module.Rx                               ''Get length of frame data
      len.byte[3] |= module.Rx
      
      bytefill(@tmparr,0,254)
      sum := 0
      bytenum := 0
  
      repeat bytenum from 0 to len.byte[3] - 1                        ''Store as much data as possible in the temp array
        tmp := module.Rx
        sum.byte[3] += tmp
        if bytenum < 254
          byte[@tmparr][bytenum] := tmp

      sum.byte[3] += module.Rx

      if sum.byte[3] <> 255                   ''Check the computed checksum and store data in queue if valid
        return -1
      else
      instack.write(len.byte[3],@tmparr)
      return 0
    return 1                                              ''Return 1 if no frame start identifier
  return 2

PUB PushFrame|pos,sum,len

  if not outstack.empty
    len := outstack.length
    bytefill(@tmparr,0,254)
  
    module.Tx($7E)                      ''Shift out frame start and length
    module.Tx($00)
    module.Tx(len)

    sum := 0
    outstack.read(@tmparr)
    
    repeat pos from 0 to len-1                                 ''Shift out frame data and work out checksum
      module.Tx(byte[@tmparr][pos])
      sum.byte[3] += byte[@tmparr][pos]

    module.Tx($FF-sum.byte[3])          ''Finalize and shift out checksum
    return 0
  return 1

PUB Listener

  repeat
    PushFrame
    PullFrame
        