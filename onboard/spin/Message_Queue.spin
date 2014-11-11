{{
/**
 * This is an object designed to hold a queue of data received from a communications system as a buffer.
 * It keeps track of which order messages are received in while storing them in whatever message
 * slot happens to be free at the time. Slot size includes a starting byte indicating slot occupancy
 * as well as a byte indicating length of the data, so slot size should be n+2, where n is the size of
 * the block of data you wish to store, in bytes.
 */
}}

VAR
  word startAddr
  word slotSize
  byte numSlots
  byte curMessage
  byte nextSlot 

PUB init(base,size,slot_size) '//initialize queue with starting values

  startAddr := base
  slotSize := slot_size
  numSlots := size / slot_size
  curMessage := 0
  nextSlot := 0

PUB write(len,data): status | slotBase,byteNum

  status := -1
  slotBase := startAddr + nextSlot*slotSize
  
  if byte[slotBase] <> 255
    byte[slotBase] := 255
    byte[slotBase][1] := len
    if len > slotSize-2
      byte[slotBase][1] := slotSize-2

    repeat byteNum from 2 to slotSize
      if byteNum == len + 2
        quit
      else
        byte[slotBase][byteNum] := byte[data][byteNum-2]

    nextSlot += 1
    if nextSlot == numSlots
      nextSlot := 0
    return 0

PUB read(output_addr): status | slotBase,byteNum,len

  status := -1
  slotBase := startAddr + curMessage*slotSize

  if byte[slotBase] == 255
    len := byte[slotBase][1]

    repeat byteNum from 2 to slotSize
      if byteNum == len + 2
        quit
      else
        byte[output_addr][byteNum-2] := byte[slotBase][byteNum]

    byte[slotBase] := 0
    curMessage += 1
    if curMessage == numSlots
      curMessage := 0
    return 0
  
PUB slotOccupied(slot)

  return byte[startAddr + slot*slotSize] == 255

PUB length

  if not empty
    return byte[startAddr + curMessage*slotSize][1]
  return -1
  
PUB slotCount

  return numSlots

PUB full

  return slotOccupied(nextSlot)
  
PUB empty

  return not slotOccupied(curMessage)
           