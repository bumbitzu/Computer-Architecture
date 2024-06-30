import time

class MemoryBus:
    def __init__(self, memory_size):
        self.memory = [0] * memory_size

    def initialize(self, init_file):
        with open(init_file, 'r') as file:
            for line in file:
                address, value = map(int, line.split())
                self.memory[address] = value
                print(f"Initialized memory at address {address} with value {value}")

    def read(self, address):
        time.sleep(0.01)  # Simulating delay for memory read
        return self.memory[address]

    def write(self, address, data):
        time.sleep(0.01)  # Simulating delay for memory write
        self.memory[address] = data


class Cache:
    def __init__(self, size):
        self.size = size
        self.cache = {}
        self.order = []
        self.enabled = True

    def read(self, address):
        if not self.enabled:
            return None
        if address in self.cache:
            self.order.remove(address)
            self.order.append(address)
            return self.cache[address]
        else:
            return None

    def write(self, address, data):
        if not self.enabled:
            return
        if address in self.cache:
            self.order.remove(address)
        elif len(self.cache) >= self.size:
            oldest_address = self.order.pop(0)
            del self.cache[oldest_address]
        self.cache[address] = data
        self.order.append(address)

    def flush(self):
        self.cache.clear()
        self.order.clear()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class CPU:
    def __init__(self, cache_size, memory_size):
        self.cache = Cache(cache_size)
        self.memory_bus = MemoryBus(memory_size)
        self.registers = [0] * 32
        self.PC = 0
        self.halted = False

    def initialize_memory(self, init_file):
        self.memory_bus.initialize(init_file)

    def execute_instructions(self, instruction_file):
        with open(instruction_file, 'r') as file:
            instructions = file.readlines()
        while not self.halted and self.PC < len(instructions):
            line = instructions[self.PC].strip()
            if line:
                self.execute_instruction(line)
            self.PC += 1

    def execute_instruction(self, line):
        parts = line.split()
        instruction = parts[0].upper()
        operands = parts[1:] if len(parts) > 1 else []

        if instruction == 'ADD':
            Rd, Rs, Rt = map(int, operands)
            self.registers[Rd] = self.registers[Rs] + self.registers[Rt]
            print(f"Executed ADD: R{Rd} <- R{Rs} + R{Rt}")

        elif instruction == 'ADDI':
            Rt, Rs, immd = int(operands[0]), int(operands[1]), int(operands[2])
            self.registers[Rt] = self.registers[Rs] + immd
            print(f"Executed ADDI: R{Rt} <- R{Rs} + {immd}")

        elif instruction == 'SUB':
            Rd, Rs, Rt = map(int, operands)
            self.registers[Rd] = self.registers[Rs] - self.registers[Rt]
            print(f"Executed SUB: R{Rd} <- R{Rs} - R{Rt}")

        elif instruction == 'SLT':
            Rd, Rs, Rt = map(int, operands)
            self.registers[Rd] = 1 if self.registers[Rs] < self.registers[Rt] else 0
            print(f"Executed SLT: R{Rd} <- R{Rs} < R{Rt}")

        elif instruction == 'BNE':
            Rs, Rt, offset = int(operands[0]), int(operands[1]), int(operands[2])
            if self.registers[Rs] != self.registers[Rt]:
                self.PC += offset
            print(f"Executed BNE: if R{Rs} != R{Rt} then PC <- PC + {offset * 4}")

        elif instruction == 'J':
            target = int(operands[0])
            self.PC = target * 4
            print(f"Executed J: PC <- {target * 4}")

        elif instruction == 'JAL':
            target = int(operands[0])
            self.registers[7] = self.PC + 1
            self.PC = target * 4
            print(f"Executed JAL: R7 <- PC + 1; PC <- {target * 4}")

        elif instruction == 'LW':
            Rt, offset, Rs = int(operands[0]), int(operands[1]), int(operands[2])
            address = self.registers[Rs] + offset
            data = self.cache.read(address) or self.memory_bus.read(address)
            self.cache.write(address, data)
            self.registers[Rt] = data
            print(f"Executed LW: R{Rt} <- MEM[R{Rs} + {offset}]")

        elif instruction == 'SW':
            Rt, offset, Rs = int(operands[0]), int(operands[1]), int(operands[2])
            address = self.registers[Rs] + offset
            data = self.registers[Rt]
            self.cache.write(address, data)
            self.memory_bus.write(address, data)
            print(f"Executed SW: MEM[R{Rs} + {offset}] <- R{Rt}")

        elif instruction == 'CACHE':
            code = int(operands[0])
            if code == 0:
                self.cache.disable()
                print("Executed CACHE: Cache disabled")
            elif code == 1:
                self.cache.enable()
                print("Executed CACHE: Cache enabled")
            elif code == 2:
                self.cache.flush()
                print("Executed CACHE: Cache flushed")

        elif instruction == 'HALT':
            self.halted = True
            print("Executed HALT: Terminate execution")

        else:
            print(f"Invalid instruction: {line}")


# Example usage:
cpu = CPU(cache_size=4, memory_size=1024)

# Create sample initialization and instruction files
init_file = 'memory_init.txt'
instruction_file = 'instructions.txt'

with open(init_file, 'w') as file:
    file.write('0 10\n')
    file.write('1 20\n')

with open(instruction_file, 'w') as file:
    file.write('ADD 2 0 1\n')
    file.write('ADDI 3 2 5\n')
    file.write('SUB 4 3 1\n')
    file.write('SLT 5 4 0\n')
    file.write('BNE 5 0 2\n')
    file.write('J 10\n')
    file.write('JAL 15\n')
    file.write('LW 6 0 1\n')
    file.write('SW 6 0 1\n')
    file.write('CACHE 2\n')
    file.write('CACHE 0\n')
    file.write('CACHE 1\n')
    file.write('HALT\n')

# Initialize memory and execute instructions
cpu.initialize_memory(init_file)
cpu.execute_instructions(instruction_file)
