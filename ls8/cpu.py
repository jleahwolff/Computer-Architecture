"""CPU functionality."""

# import sys

# ----------------------------- attempt 1
# class CPU:
#     """Main CPU class."""

#     def __init__(self):
#         """Construct a new CPU."""
#         self.ram = [0] * 256
#         self.reg = [0] * 8
#         self.pc = 0
#         self.sp = 255
#         self.is_running = True


#     def load(self, p):
#         """Load a program into memory."""

#         address = 0

#         # For now, we've just hardcoded a program:

#         # program = [
#         #     # From print8.ls8
#         #     0b10000010, # LDI R0,8
#         #     0b00000000,
#         #     0b00001000,
#         #     0b01000111, # PRN R0
#         #     0b00000000,
#         #     0b00000001, # HLT
#         # ]
    
#         with open(p) as program:
#             for line in program:
#                 instruction = line.split('#')[0].strip()
#                 if instruction != '':
#                     try:
#                         self.ram[address] = int(instruction, 2)
#                         address += 1
#                     except IndexError:
#                         print('Memory overflow!')
#                         return

#         # for instruction in program:
#         #     self.ram[address] = instruction
#         #     address += 1


#     def alu(self, op, reg_a, reg_b):
#         """ALU operations."""

#         if op == "ADD":
#             self.reg[reg_a] += self.reg[reg_b]
#         #elif op == "SUB": etc
#         else:
#             raise Exception("Unsupported ALU operation")

#     def trace(self):
#         """
#         Handy function to print out the CPU state. You might want to call this
#         from run() if you need help debugging.
#         """

#         print(f"TRACE: %02X | %02X %02X %02X |" % (
#             self.pc,
#             #self.fl,
#             #self.ie,
#             self.ram_read(self.pc),
#             self.ram_read(self.pc + 1),
#             self.ram_read(self.pc + 2)
#         ), end='')

#         for i in range(8):
#             print(" %02X" % self.reg[i], end='')

#         print()

#     def run(self):
#         """Run the CPU."""
#         while self.is_running:
#             # read the ram at that address and find if it is a command or value
#             instruction = self.ram_read(self.pc)
#             if instruction == 0b10000010:  # LDI
#                 reg_address = self.ram_read(self.pc + 1)
#                 reg_value = self.ram_read(self.pc + 2)
#                 self.reg[reg_address] = reg_value
#                 self.pc += 3
#             elif instruction == 0b10100010:  # MULT
#                 # store values in regA and regB
#                 regA = self.ram_read(self.pc + 1)
#                 regB = self.ram_read(self.pc + 2)
#                 # store product in regA
#                 self.reg[regA] = self.reg[regA] * self.reg[regB]
#                 self.pc += 3
#             elif instruction == 0b01000101:  # PUSH
#                 # push to R7
#                 self.sp -= 1
#                 mdr = self.reg[self.ram_read(self.pc + 1)]
#                 self.ram_write(self.sp, mdr)
#                 self.pc += 2
#             elif instruction == 0b01000110:  # POP
#                 # pop to R8
#                 regA = self.ram_read(self.pc + 1)
#                 mdr = self.ram_read(self.sp)
#                 self.reg[regA] = mdr
#                 self.pc += 2
#                 self.sp += 1
#             elif instruction == 0b01000111:  # PRN
#                 print(int(self.reg[self.ram_read(self.pc + 1)]))
#                 self.pc += 2
#             elif instruction == 0b00000001:  # HLT
#                 self.is_running = False
#             else:
#                 self.pc += 1

#             if self.pc > 255:
#                 self.is_running = False

#     def ram_read(self, mar):
#         return self.ram[mar]

#     def ram_write(self, mdr, value):
#         self.ram[mdr] = value
# --------------------------------------------------------------
"""CPU functionality."""

import sys

# instruction to opcode
HLT = 0b00000001    # Exit emulator
LDI = 0b10000010    # Set value of register
PRN = 0b01000111    # Print value at register
MUL = 0b10100010    # Multiply values of two registers
PUSH = 0b01000101   # Push value in given register on stack
POP = 0b01000110    # Pop value at top of stack into given register
CALL = 0b01010000   # Call subroutine at address stored in register
RET = 0b00010001    # Return from subroutine by popping PC from stack
ADD = 0b10100000    # Add the value of two registers and store in register A
CMP = 0b10100111    # Compare the values of two registers and set the flag
JMP = 0b01010100    # Set the PC (jump) to the address in the given register
JEQ = 0b01010101    # If the equal flag is true, jump to address in register
JNE = 0b01010110    # If the equal flag is false, jump to address in register


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # holds 256 bytes of memory
        self.ram = [0] * 256
        # 8 general-purpose registers + stack pointer
        self.reg = [0] * 7 + [0xF4]
        # program counter, special-purpose register
        self.pc = 0

        self.running = False

        self.fl = 0b00000000
# HLT
    def hlt_handler(self, a, b):
        self.running = False
# LDI
    def ldi_handler(self, a, b):
        self.reg[a] = b
# PRN
    def prn_handler(self, a, b):
        print(self.reg[a])
# MUL
    def mul_handler(self, a, b):
        self.alu('MUL', a, b)
# PUSH
    def push_handler(self, a, b):
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.reg[a])
# POP
    def pop_handler(self, a, b):
        self.reg[a] = self.ram_read(self.reg[7])
        self.reg[7] += 1
# CALL
    def call_handler(self, a, b):
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.pc + 2)
        self.pc = self.reg[a]
# RET
    def ret_handler(self, a, b):
        self.pc = self.ram_read(self.reg[7])
        self.reg[7] += 1
# ADD
    def add_handler(self, a, b):
        self.alu('ADD', a, b)
# CMP
    def cmp_handler(self, a, b):
        self.alu('CMP', a, b)
        # print('flag is', bin(self.fl))
# JMP
    def jmp_handler(self, a, b):
        self.pc = self.reg[a]
# JEQ
    def jeq_handler(self, a, b):
        if self.fl & 0b00000001:
            self.pc = self.reg[a]
        else:
            self.pc += 2
# JNE
    def jne_handler(self, a, b):
        if (self.fl & 0b00000001) == 0:
            self.pc = self.reg[a]
        else:
            self.pc += 2

    def exec(self, instruction, a=None, b=None):
        # set up branch table
        dispatch = {
            HLT: self.hlt_handler,
            LDI: self.ldi_handler,
            PRN: self.prn_handler,
            MUL: self.mul_handler,
            PUSH: self.push_handler,
            POP: self.pop_handler,
            CALL: self.call_handler,
            RET: self.ret_handler,
            ADD: self.add_handler,
            CMP: self.cmp_handler,
            JMP: self.jmp_handler,
            JEQ: self.jeq_handler,
            JNE: self.jne_handler
        }

        dispatch[instruction](a, b)

    def load(self, file_path: str):
        """Load a program into memory."""
        address = 0

        with open(file_path) as file:
            for line in file:
                if line == '\n' or line[0] == '#':
                    continue
                else:
                    self.ram[address] = int(line.split()[0], 2)

                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        # arithmetic logic unit

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP": #------- SPRINT MVP
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100

            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010

            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            # read the memory address stored in register PC
            # then store in ir, the instruction register
            ir = self.ram_read(self.pc)

            # read bytes at PC+1 and PC+2 in case instruction needs them
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            try:
                self.exec(ir, operand_a, operand_b)

                if ((ir & 0b00010000) >> 4) == 0:
                    n_operands = (ir & 0b11000000) >> 6
                    n_move_pc = n_operands + 1
                    self.pc += n_move_pc
            except:
                print(f'Unknown instruction {bin(ir)} at address {self.pc}')
                sys.exit(1)

    def ram_read(self, address: int):
        """Return the value stored at the address."""
        return self.ram[address]

    def ram_write(self, address: int, data):
        self.ram[address] = data