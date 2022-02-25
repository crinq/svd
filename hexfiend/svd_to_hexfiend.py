import xml.etree.ElementTree as ET
import sys
import os

#svd = open(sys.argv[1])
tcl = open(sys.argv[2], 'w')

tree = ET.parse(sys.argv[1])
root = tree.getroot()

class field:
  name = ""
  doc = ""
  addr = 0
  len = 0

class reg:
  name = ""
  doc = ""
  addr = 0
  len = 0
  reset = 0
  fields = []

class periph:
  name = ""
  addr = 0
  regs = []

class cpu:
  periphs = []

core = cpu()

for p in root.find("peripherals").findall("peripheral"):
  tp = periph()
  tp.regs = []
  tp.name = p.find("name").text
  tp.addr = int(p.find("baseAddress").text, 16)
  if "derivedFrom" in p.attrib:
    name = p.attrib["derivedFrom"]
    for per in core.periphs:
      if per.name == name:
        for re in per.regs:
          tr = reg()
          tr.fields = []
          tr.name = re.name
          tr.doc = re.doc
          tr.addr = re.addr
          tr.len = re.len
          tr.reset = re.reset
          for f in re.fields:
            tf = field()
            tf.name = f.name
            tf.doc = f.doc
            tf.addr = f.addr
            tf.len = f.len
            tr.fields.append(tf)
          tp.regs.append(tr)
  else:
    for c in p.find("registers").findall("cluster"):
      index = c.find("dimIndex").text.split(",")
      offset = int(c.find("addressOffset").text, 16)
      inc = int(c.find("dimIncrement").text, 16)
      for cnt, i in enumerate(index):
        for r in c.findall("register"):
          tr = reg()
          tr.fields = []
          tr.name = r.find("name").text + i
          tr.doc = r.find("description").text
          tr.addr = int(r.find("addressOffset").text, 16) + offset + inc * cnt
          tr.len = int(r.find("size").text, 16)
          tr.reset = int(r.find("resetValue").text, 16)
          if r.find("fields"):
            for f in r.find("fields").findall("field"):
              tf = field()
              tf.name = f.find("name").text
              tf.doc = f.find("description").text
              tf.addr = int(f.find("bitOffset").text)
              tf.len = int(f.find("bitWidth").text)
              tr.fields.append(tf)
            tp.regs.append(tr)

    for r in p.find("registers").findall("register"):
      index = [""]
      inc = 0
      offset = int(r.find("addressOffset").text, 16)
      if r.find("dim") != None:
        index = r.find("dimIndex").text.split(",")
        inc = int(r.find("dimIncrement").text, 16)

      for cnt, i in enumerate(index):
        tr = reg()
        tr.fields = []
        tr.name = r.find("name").text.rstrip("%s") + i
        tr.doc = r.find("description").text
        tr.addr = offset + inc * cnt
        tr.len = int(r.find("size").text, 16)
        tr.reset = int(r.find("resetValue").text, 16)
        if r.find("fields"):
          for f in r.find("fields").findall("field"):
            tf = field()
            tf.name = f.find("name").text
            tf.doc = f.find("description").text
            tf.addr = int(f.find("bitOffset").text)
            tf.len = int(f.find("bitWidth").text)
            tr.fields.append(tf)
          tp.regs.append(tr)
  cpu.periphs.append(tp)




address_offset = 0x40000000

tcl.write("little_endian\n")

def addr_key(p):
  return p.addr

for p in sorted(core.periphs, key = addr_key):
  if p.addr >= 0x40000000 and p.addr <= 0x40040000:
    tcl.write("goto " + str(p.addr - address_offset) + "\n")
    tcl.write("section -collapsed \"" + p.name + " @" + hex(p.addr) + "\" {\n")
    for r in sorted(p.regs, key = addr_key):
      tcl.write("  goto " + str(p.addr + r.addr - address_offset) + "\n")
      if len(r.fields) > 0:
        tcl.write("  section -collapsed \"" + r.name + " @" + hex(r.addr) + "\" {\n")
        tcl.write("    uint32 -hex \"" + r.name + "\"\n")
        tcl.write("    move -4\n")
        for f in sorted(r.fields, key = addr_key):
          tcl.write("    uint32_bits ")
          for i in range(f.len):
            tcl.write(str(f.addr + f.len - i - 1) + ",")
          tcl.seek(tcl.tell() - 1, os.SEEK_SET)
          tcl.write(" \"" + f.name + "(" + str(f.addr) + ":" + str(f.addr + f.len - 1) + ")\"\n")
          tcl.write("    move -4\n")
        tcl.write("  }\n")
      else:
        tcl.write("  uint32 \"" + r.name + "\"\n")
    tcl.write("}\n")

  # section "TIM2" {
  # section "CR1" {
  #   uint32_bits 0 "CEN"
  #   move -4