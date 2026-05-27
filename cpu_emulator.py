import time

class CustomCPU:
    def __init__(self, memory_size=256, vram_size=100):
        # 1. Registers
        self.ACC = 0        # Accumulator
        self.PC = 0         # Program Counter
        self.SP = memory_size - 1  # Stack Pointer (starts at the end of memory)
        self.IR = 0         # Instruction Register
        self.FLAG_ZF = False # Zero Flag
        self.running = False

        # 2. Memory
        self.memory = [0] * memory_size
        self.vram_start = memory_size - vram_size - 1 # Start of VRAM
        self.vram_size = vram_size
        
        # 3. Instruction Set Mapping (OpCodes)
        self.OPCODES = {
            0x00: "NOP",
            0x01: "LOAD_CONST",
            0x02: "LOAD_MEM",
            0x03: "STORE_MEM",
            0x04: "ADD",
            0x05: "SUB",
            0x06: "MUL",
            0x07: "DIV",
            0x08: "JMP",
            0x09: "JZ",
            0x0A: "JNZ",
            0x0B: "CMP",
            0x0C: "PUSH",
            0x0D: "POP",
            0x0E: "CALL",
            0x0F: "RET",
            0x10: "VRAM_SET_PIXEL",
            0x11: "HALT"
        }

    def load_program(self, program):
        """Loads a list of OpCodes into memory starting from address 0."""
        for i, opcode in enumerate(program):
            if i < self.vram_start:
                self.memory[i] = opcode
            else:
                raise Exception("Program exceeds memory limit before VRAM.")

    def fetch(self):
        """Fetch the next instruction from memory using PC."""
        if self.PC < len(self.memory):
            self.IR = self.memory[self.PC]
            self.PC += 1
        else:
            self.running = False

    def decode_and_execute(self):
        """Decode the instruction in IR and execute it."""
        opcode_name = self.OPCODES.get(self.IR, "UNKNOWN")
        
        if opcode_name == "NOP":
            pass
        
        elif opcode_name == "LOAD_CONST":
            value = self.memory[self.PC]
            self.PC += 1
            self.ACC = value
            
        elif opcode_name == "LOAD_MEM":
            address = self.memory[self.PC]
            self.PC += 1
            self.ACC = self.memory[address]
            
        elif opcode_name == "STORE_MEM":
            address = self.memory[self.PC]
            self.PC += 1
            self.memory[address] = self.ACC
            
        elif opcode_name == "ADD":
            address = self.memory[self.PC]
            self.PC += 1
            self.ACC += self.memory[address]
            self.FLAG_ZF = (self.ACC == 0)
            
        elif opcode_name == "SUB":
            address = self.memory[self.PC]
            self.PC += 1
            self.ACC -= self.memory[address]
            self.FLAG_ZF = (self.ACC == 0)
            
        elif opcode_name == "MUL":
            address = self.memory[self.PC]
            self.PC += 1
            self.ACC *= self.memory[address]
            self.FLAG_ZF = (self.ACC == 0)
            
        elif opcode_name == "DIV":
            address = self.memory[self.PC]
            self.PC += 1
            if self.memory[address] != 0:
                self.ACC //= self.memory[address]
            else:
                raise Exception("Division by zero.")
            self.FLAG_ZF = (self.ACC == 0)
            
        elif opcode_name == "JMP":
            address = self.memory[self.PC]
            self.PC = address
            
        elif opcode_name == "JZ":
            address = self.memory[self.PC]
            if self.FLAG_ZF:
                self.PC = address
            else:
                self.PC += 1
                
        elif opcode_name == "JNZ":
            address = self.memory[self.PC]
            if not self.FLAG_ZF:
                self.PC = address
            else:
                self.PC += 1
                
        elif opcode_name == "CMP":
            address = self.memory[self.PC]
            self.PC += 1
            self.FLAG_ZF = (self.ACC == self.memory[address])
            
        elif opcode_name == "PUSH":
            value = self.memory[self.PC] # Assuming value for now, can be memory too
            self.PC += 1
            self.memory[self.SP] = value
            self.SP -= 1
            
        elif opcode_name == "POP":
            self.SP += 1
            self.ACC = self.memory[self.SP]
            
        elif opcode_name == "CALL":
            address = self.memory[self.PC]
            self.PC += 1
            # Push return address (current PC) to stack
            self.memory[self.SP] = self.PC
            self.SP -= 1
            self.PC = address
            
        elif opcode_name == "RET":
            self.SP += 1
            self.PC = self.memory[self.SP]
            
        elif opcode_name == "VRAM_SET_PIXEL":
            x = self.memory[self.PC]
            y = self.memory[self.PC + 1]
            color = self.memory[self.PC + 2]
            self.PC += 3
            # Simplified VRAM mapping: vram_start + (y * width + x)
            # For simplicity, assume width is 10
            vram_index = self.vram_start + (y * 10 + x)
            if vram_index < len(self.memory):
                self.memory[vram_index] = color
            
        elif opcode_name == "HALT":
            self.running = False
            
        else:
            print(f"Unknown OpCode: {self.IR}")
            self.running = False

    def run(self, debug=False):
        """Main Fetch-Decode-Execute Loop."""
        self.running = True
        while self.running:
            if debug:
                print(f"PC: {self.PC:02X} | IR: {self.IR:02X} | ACC: {self.ACC:02X} | ZF: {self.FLAG_ZF}")
            self.fetch()
            self.decode_and_execute()
            # time.sleep(0.1) # Optional: slow down for observation

    def get_vram(self):
        """Return the VRAM section of memory."""
        return self.memory[self.vram_start : self.vram_start + self.vram_size]

# --- Example Usage ---
if __name__ == "__main__":
    cpu = CustomCPU()
    
    # Program: 
    # LOAD_CONST 10 (0x01 0x0A)
    # STORE_MEM 50 (0x03 0x32)
    # LOAD_CONST 5 (0x01 0x05)
    # ADD 50 (0x04 0x32)
    # HALT (0x11)
    
    program = [0x01, 0x0A, 0x03, 0x32, 0x01, 0x05, 0x04, 0x32, 0x11]
    
    cpu.load_program(program)
    print("Starting CPU...")
    cpu.run(debug=True)
    print(f"Final ACC value: {cpu.ACC}") # Should be 15
