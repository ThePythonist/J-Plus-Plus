import pygame, sys, copy, tkinter, random, time
from pygame.locals import *
from tkinter import filedialog

class Counter:
    def __init__(self):
        self.page = 0
        self.pos = 0
        self.absolute = 0
    def get(self):
        self.absolute += 1
        self.pos = self.absolute%5
        self.page = self.absolute//5
        return self.absolute-1
    def new_page(self):
        if self.pos > 0:
            self.page += 1
            self.pos = 0
            self.absolute = self.page * 5

class OpenOrNew(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.read = []
        self.initUI()
        self.centerWindow()

    def centerWindow(self):
        w = 290
        h = 100
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):
        self.parent.title("Open or New")
        self.pack(fill=tkinter.BOTH, expand=1)
        tkinter.Button(self, bg="white", text="Open", command=self.open).pack(pady=10)
        tkinter.Button(self, bg="white", text="New", command=self.parent.destroy).pack(pady=10)

    def open(self):
        f = filedialog.askopenfile(mode="r", defaultextension=".jpp")
        if f is not None:
            self.read = f.readlines()
            f.close()
            self.parent.destroy()

read = []

if len(sys.argv) <= 1:
    root = tkinter.Tk()
    app = OpenOrNew(root)
    root.mainloop()
    read = app.read
else:
    load = open(" ".join(sys.argv[1:]))
    read = load.readlines()
    load.close()
pygame.init()



def greaterOf(x, y):
    if y > x:
        return y
    return x


def orderByInputNum(inputs):
    changes = -1
    while changes != 0:
        changes = 0
        for i in range(len(inputs) - 1):
            if inputs[i]["inputNum"] > inputs[i + 1]["inputNum"]:
                temp = inputs[i]
                inputs[i] = inputs[i + 1]
                inputs[i + 1] = temp
                changes += 1
    return inputs


def run(block, links, blocks):
    try:
        if type(block) == type(Literal("string", "loem ipsum dolor sit amet", [0, 0])):
            if block.dataType == "int":
                return [int(block.value)]
            if block.dataType == "float":
                return [float(block.value)]
            if block.dataType == "boolean":
                return [block.value == "True"]
            return [block.value]
        inputs = list()
        outputs = list()
        for link in links:
            if link.child == block:
                inputs.append({"block": link.parent,
                               "outputNum": link.outputNum,
                               "inputNum": link.inputNum})
        inputs = copy.copy(orderByInputNum(inputs))
        if "variable" in block.plugins:
            if block.value is None:
                block.value = run(inputs[0]["block"], links, blocks)[inputs[0]["outputNum"]]
            return [block.value]
        for i in range(len(inputs)):
            inputs[i] = run(inputs[i]["block"], links, blocks)[inputs[i]["outputNum"]]
        if block.name == "print":
            print(inputs[0])
        elif block.name == "add":
            outputs.append(inputs[0] + inputs[1])
        elif block.name == "subtract":
            outputs.append(inputs[0] - inputs[1])
        elif block.name == "multiply":
            outputs.append(inputs[0] * inputs[1])
        elif block.name == "divide":
            outputs.append(inputs[0] / inputs[1])
        elif block.name == "modulus":
            outputs.append(inputs[0] % inputs[1])
        elif block.name == "str":
            outputs.append(str(inputs[0]))
        elif block.name == "int":
            outputs.append(int(inputs[0]))
        elif block.name == "float":
            outputs.append(float(inputs[0]))
        elif block.name == "boolean":
            outputs.append(inputs[0] == "True")
        elif block.name == "input":
            outputs.append(input(inputs[0]))
        elif block.name == "length":
            outputs.append(len(inputs[0]))
        elif block.name == "if":
            outputs.append(inputs[0])
        elif block.name == "equal":
            outputs.append(inputs[0] == inputs[1])
        elif block.name == "not equal":
            outputs.append(inputs[0] != inputs[1])
        elif block.name == "less than":
            outputs.append(inputs[0] < inputs[1])
        elif block.name == "less than or equal":
            outputs.append(inputs[0] <= inputs[1])
        elif block.name == "greater than":
            outputs.append(inputs[0] > inputs[1])
        elif block.name == "greater than or equal":
            outputs.append(inputs[0] >= inputs[1])
        elif block.name == "while":
            outputs.append(inputs[0])
        elif block.name == "for":
            outputs.append(inputs[1])
        elif block.name == "and":
            outputs.append(inputs[0] and inputs[1])
        elif block.name == "or":
            outputs.append(inputs[0] or inputs[1])
        elif block.name == "not":
            outputs.append(not inputs[0])
        elif block.name == "nand":
            outputs.append(not (inputs[0] and inputs[1]))
        elif block.name == "nor":
            outputs.append(not (inputs[0] or inputs[1]))
        elif block.name == "set":
            for i in links:
                if i.child == block:
                    if "variable" in i.parent.plugins:
                        i.parent.value = inputs[1]
        elif block.name == "random":
            outputs.append(random.randint(inputs[0],inputs[1]))
        elif block.name == "delay":
            time.sleep(inputs[0])
        elif "method" in block.plugins:
            outputs = runMethod([i for i in blocks if "methodblock" in i.plugins and i.name == block.name][-1], blocks, inputs, links)
        return outputs
    except Exception as e:
        print("", e, file=sys.stderr)
        block.error = True
        return []

def runMethod(methodBlock, blocks, inputs, links):
    inputVars = list()
    for i in range(len(inputs)):
        var = Block("",0,1,[0,0],["variable"])
        var.value = inputs[i]
        for link in links:
            if link.parent == methodBlock:
                if link.outputNum == i:
                    link.parent = var
                    link.outputNum = 0
        inputVars.append(var)

    outputVars = list()
    for i in range(methodBlock.numOfOutputsX):
        var = Block("",1,0,[0,0],["variable"])
        var.value = None
        for link in links:
            if link.child == methodBlock:
                if link.inputNum == i:
                    link.child = var
                    link.inputNum = 0
        outputVars.append(var)

    skip = False
    skipElse = False
    skipWhile = False
    forBlock = None
    order = methodBlock.order + outputVars
    numOfIfs = 0
    numOfEnds = 0
    numOfElses = 0
    blockToReturn = -1
    for block in blocks:
        if "variable" in block.plugins:
            block.value = None
    blockIndex = 0
    while blockIndex < len(order):
        pygame.display.update()
        toBreak = False
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    toBreak = True
        if toBreak:
            break
        block = order[blockIndex]
        if skip or skipElse or skipWhile:
            if block.name in ["if", "while", "for"]:
                numOfIfs += 1
            if block.name == "end":
                numOfEnds += 1
                if numOfEnds == numOfIfs:
                    skip = False
                    skipElse = False
                    skipWhile = False
            if block.name == "else" and skipElse == False and skipWhile == False:
                numOfElses += 1
                if numOfElses == numOfIfs:
                    skip = False
            blockIndex += 1
            continue
        successful = run(block, links, blocks)
        if len(successful) > 0:
            successful = successful[0]
        if block.name == "end":
            if blockToReturn != -1:
                blockIndex = blockToReturn
                blockToReturn = -1
                if forBlock is not None:
                    for link in links:
                        if link.child == forBlock:
                            if link.inputNum == 0:
                                link.parent.value = int(link.parent.value)+1
            else:
                blockIndex += 1
            continue
        if block.name == "if":
            if not successful:
                skip = True
                numOfIfs = 1
                numOfEnds = 0
                numOfElses = 0
        if block.name == "else":
            skipElse = True
            numOfIfs = 1
            numOfEnds = 0
        if block.name == "while" or block.name == "for":
            if not successful:
                skipWhile = True
                numOfIfs = 1
                numOfEnds = 0
            else:
                blockToReturn = blockIndex
                if block.name == "for":
                    forBlock = block
        blockIndex += 1
    for i in range(len(inputVars)):
        for link in links:
            if link.parent == inputVars[i]:
                link.parent = methodBlock
                link.outputNum = i
    for i in range(len(outputVars)):
        for link in links:
            if link.child == outputVars[i]:
                link.child = methodBlock
                link.inputNum = i
    return [x.value for x in outputVars]

class SetMethodBlock(tkinter.Frame):
    def __init__(self, parent, block=None):
        tkinter.Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.enteredName = tkinter.StringVar()
        self.numOfInputs = tkinter.StringVar()
        self.numOfOutputs = tkinter.StringVar()
        if block is not None:
            self.enteredName.set(block.name)
            self.numOfInputs.set(block.numOfInputs)
            self.numOfOutputs.set(block.numOfOutputs)
        self.initUI()
        self.centerWindow()

    def centerWindow(self):
        w = 290
        h = 300
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):
        self.parent.title("Set Name")
        self.pack(fill=tkinter.BOTH, expand=1)
        tkinter.Label(self, bg="white", text="Enter Name:").pack(pady=10)
        tkinter.Entry(self, textvariable=self.enteredName, bg="white").pack(pady=10)
        tkinter.Label(self, bg="white", text="Number of Inputs:").pack(pady=10)
        tkinter.Entry(self, textvariable=self.numOfOutputs, bg="white").pack(pady=10)
        tkinter.Label(self, bg="white", text="Number of Outputs:").pack(pady=10)
        tkinter.Entry(self, textvariable=self.numOfInputs, bg="white").pack(pady=10)
        tkinter.Button(self, bg="white", text="Add", command=self.parent.destroy).pack()


class SetName(tkinter.Frame):
    def __init__(self, parent, block=None):
        tkinter.Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.enteredText = tkinter.StringVar()
        if block is not None:
            self.enteredText.set(block.name)
        self.initUI()
        self.centerWindow()

    def centerWindow(self):
        w = 290
        h = 150
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):
        self.parent.title("Set Name")
        self.pack(fill=tkinter.BOTH, expand=1)
        tkinter.Label(self, bg="white", text="Enter Name:").pack(pady=10)
        tkinter.Entry(self, textvariable=self.enteredText, bg="white").pack(pady=10)
        tkinter.Button(self, bg="white", text="Add", command=self.parent.destroy).pack()


class SetLiteral(tkinter.Frame):
    def __init__(self, parent, literal=None, error=None):
        tkinter.Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.enteredValue = tkinter.StringVar()
        self.enteredType = tkinter.StringVar()
        if error is not None:
            literal = Literal(error[1], error[0], [0,0])
        if literal is None:
            self.enteredType.set("string")
        else:
            self.enteredType.set(literal.dataType)
            self.enteredValue.set(literal.value)
        self.error = error
        self.initUI()
        self.centerWindow()

    def centerWindow(self):
        w = 290
        h = 250
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):
        self.parent.title("Set Literal Value")
        self.pack(fill=tkinter.BOTH, expand=1)
        if self.error is not None:
            tkinter.Label(self, bg="white", text=self.error[0]+" can not be "+self.error[1]).pack(pady=10)
        tkinter.Label(self, bg="white", text="Enter Value:").pack(pady=10)
        tkinter.Entry(self, textvariable=self.enteredValue, bg="white").pack(pady=10)
        tkinter.Label(self, bg="white", text="Select Data Type:").pack(pady=10)
        tkinter.OptionMenu(self, self.enteredType, "string", "int", "float", "boolean").pack(pady=10)
        tkinter.Button(self, bg="white", text="Add", command=self.parent.destroy).pack()


class SetConditional(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.name = tkinter.StringVar()
        self.name.set("equal")
        self.initUI()
        self.centerWindow()

    def centerWindow(self):
        w = 290
        h = 200
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):
        self.parent.title("Set Conditional Type")
        self.pack(fill=tkinter.BOTH, expand=1)
        tkinter.Label(self, bg="white", text="Select Conditional Type:").pack(pady=10)
        tkinter.OptionMenu(self, self.name, "equal", "not equal", "less than", "less than or equal", "greater than",
                           "greater than or equal").pack(pady=10)
        tkinter.Button(self, bg="white", text="Add", command=self.parent.destroy).pack()


class MenuItem:
    def __init__(self, name, numOfInputs, numOfOutputs, myId, plugins=None):
        if plugins is None:
            plugins = []
        self.plugins = plugins
        self.name = name
        self.numOfInputs = numOfInputs
        self.numOfOutputs = numOfOutputs
        self.myId = myId
        self.page = int(myId / 5)
        if "literal" in plugins:
            self.block = Literal("string", self.name, [0, 0])
        elif "methodblock" in plugins:
            self.block = MethodBlock(self.name, self.numOfInputs, numOfOutputs, [0,0], [50,50], plugins=plugins)
        else:
            self.block = Block(self.name, self.numOfInputs, self.numOfOutputs, [0, 0], plugins=plugins)
        self.relPos = self.myId - self.page * 5
        self.pos = [750 + (250 / 2) - self.block.get_width() / 2, 60 + (self.relPos * (20 + self.block.get_height()))]
        if "literal" in plugins:
            self.pos[1] += 40
        self.block.pos = self.pos

    def display(self, screen):
        self.block.display(screen)

    def get_new(self):
        blockToAdd = copy.copy(self.block)
        blockToAdd.pos = [0, 0]
        if "methodblock" in self.plugins:
            blockToAdd.size = copy.copy(blockToAdd.size)
            blockToAdd.order = list()
        global blockId
        if "set name" in self.plugins:
            if "literal" in self.plugins:
                valid = False
                error = None
                while not valid:
                    root = tkinter.Tk()
                    app = SetLiteral(root, error=error)
                    root.mainloop()
                    theType = app.enteredType.get()
                    value = app.enteredValue.get()
                    valid = True
                    try:
                        if theType == "int":
                            value = str(int(value))
                        if theType == "float":
                            value = str(float(value))
                        if theType == "boolean":
                            value = str(value == "True")
                    except:
                        valid = False
                        error = [value, theType]
                    blockToAdd.value = value
                    blockToAdd.dataType = theType
                    blockToAdd.reset_label()
            elif blockToAdd.name == "if":
                root = tkinter.Tk()
                app = SetConditional(root)
                root.mainloop()
                blockToAdd.name = app.name.get()
            elif "methodblock" in self.plugins:
                root = tkinter.Tk()
                app = SetMethodBlock(root)
                root.mainloop()
                blockToAdd.name = app.enteredName.get()
                try:
                    blockToAdd.numOfInputs = int(app.numOfInputs.get())
                    blockToAdd.numOfOutputsX = int(app.numOfInputs.get())
                except:
                    blockToAdd.numOfInputs = 0
                    blockToAdd.numOfOutputsX = 0
                try:
                    blockToAdd.numOfOutputs = int(app.numOfOutputs.get())
                    blockToAdd.numOfInputsX = int(app.numOfOutputs.get())
                except:
                    blockToAdd.numOfOutputs = 0
                    blockToAdd.numOfInputsX = 0
                blockToAdd.size[0] = greaterOf(blockToAdd.size[0], greaterOf(50*blockToAdd.numOfInputs, 50*blockToAdd.numOfOutputs))
            elif "method" in self.plugins:
                root = tkinter.Tk()
                app = SetMethodBlock(root)
                root.mainloop()
                blockToAdd.name = app.enteredName.get()
                try:
                    blockToAdd.numOfInputs = int(app.numOfOutputs.get())
                except:
                    blockToAdd.numOfInputs = 0
                try:
                    blockToAdd.numOfOutputs = int(app.numOfInputs.get())
                except:
                    blockToAdd.numOfOutputs = 0
            else:
                root = tkinter.Tk()
                app = SetName(root)
                root.mainloop()
                blockToAdd.name = app.enteredText.get()
        blockToAdd.blockId = blockId
        blockId += 1
        return blockToAdd


blockId = 0

class MethodBlock:
    def __init__(self, name, numOfInputs, numOfOutputs, pos, size, plugins=None, defaultBlockId=None):
        self.name = name
        self.numOfInputs = numOfInputs
        self.numOfOutputs = numOfOutputs
        self.numOfInputsX = numOfOutputs
        self.numOfOutputsX = numOfInputs
        global blockId
        if defaultBlockId is None:
            self.blockId = blockId
            blockId += 1
        else:
            self.blockId = defaultBlockId
        self.pos = pos
        self.size = size
        self.activeInput = -1
        self.activeOutput = -1
        self.font = pygame.font.SysFont("timesnewroman", 20, 1)
        if plugins is None:
            plugins = list()
        self.plugins = plugins
        self.order = list()
    def display(self, screen):
        label = self.font.render(self.name, 1, (0,0,255))
        for i in range(self.numOfInputs):
            if i == self.activeInput:
                pygame.draw.rect(screen, (255, 0, 0), Rect(self.pos[0] + 50 * i + 15, self.pos[1]+self.get_height()-21, 20, 21), 0)
            pygame.draw.rect(screen, (0, 0, 0), Rect(self.pos[0] + 50 * i + 15, self.pos[1]+self.get_height()-21, 20, 21), 2)
        for i in range(self.numOfOutputs):
            if i == self.activeOutput:
                pygame.draw.rect(screen, (255, 0, 0), Rect(self.pos[0] + 50 * i + 15, self.pos[1], 20, 21), 0)
            pygame.draw.rect(screen, (0, 0, 0), Rect(self.pos[0] + 50 * i + 15, self.pos[1], 20, 21), 2)
        pygame.draw.rect(screen, (0,0,0), Rect(self.pos[0], self.pos[1]+20, self.size[0], self.size[1]), 2)
        screen.blit(label, (self.pos[0]+self.size[0]/2-label.get_width()/2,self.pos[1]-5-label.get_height()))
    def get_width(self):
        return self.size[0]
    def get_height(self):
        return self.size[1]+40
    def change_name(self):
        root = tkinter.Tk()
        app = SetMethodBlock(root, self)
        root.mainloop()
        self.name = app.enteredName.get()
        try:
            self.numOfInputs = int(app.numOfInputs.get())
            self.numOfOutputsX = int(app.numOfInputs.get())
        except:
            self.numOfInputs = 0
            self.numOfOutputsX = 0
        try:
            self.numOfOutputs = int(app.numOfOutputs.get())
            self.numOfInputsX = int(app.numOfOutputs.get())
        except:
            self.numOfOutputs = 0
            self.numOfInputsX = 0
        self.size[0] = greaterOf(self.size[0], greaterOf(50*self.numOfInputs, 50*self.numOfOutputs))


class Literal:
    def __init__(self, dataType, value, pos, defaultBlockId=None):
        self.dataType = dataType
        global blockId
        if defaultBlockId is None:
            self.blockId = blockId
            blockId += 1
        else:
            self.blockId = defaultBlockId
        self.value = value
        self.font = pygame.font.SysFont("timesnewroman", 20, 1)
        self.pos = pos
        if dataType == "string":
            self.label = self.font.render("\"" + self.value + "\"", 1, (0, 0, 255))
        else:
            self.label = self.font.render(self.value, 1, (0, 0, 255))
        self.numOfInputs = 0
        self.numOfOutputs = 1
        self.numOfInputsX = 0
        self.numOfOutputsX = 1
        self.plugins = list()
        self.activeInput = -1
        self.activeOutput = -1
        self.name = ""
        self.error = False

    def display(self, screen):
        screen.blit(self.label, [self.pos[0] + 10, self.pos[1] + 20])
        colour = (0, 255, 0)
        if self.activeOutput == 0:
            colour = (255, 0, 0)
        pygame.draw.rect(screen, colour, Rect(self.pos[0] + 15, self.pos[1] + 20 + self.label.get_height(), 20, 20))
        pygame.draw.rect(screen, (0, 0, 0), Rect(self.pos[0] + 15, self.pos[1] + 20 + self.label.get_height(), 20, 20),
                         2)

    def get_width(self):
        return self.label.get_width() + 20

    def get_height(self):
        return self.label.get_height() + 40

    def reset_label(self):
        if self.dataType == "string":
            self.label = self.font.render("\"" + self.value + "\"", 1, (0, 0, 255))
        else:
            self.label = self.font.render(self.value, 1, (0, 0, 255))

    def change_name(self):
        valid = False
        error = None
        while not valid:
            root = tkinter.Tk()
            app = SetLiteral(root, self, error=error)
            root.mainloop()
            theType = app.enteredType.get()
            value = app.enteredValue.get()
            valid = True
            try:
                if theType == "int":
                    value = str(int(value))
                if theType == "float":
                    value = str(float(value))
                if theType == "boolean":
                    value = str(value == "True")
            except:
                valid = False
                error = [value, theType]
            self.value = value
            self.dataType = theType
            self.reset_label()


class Block:
    def __init__(self, name, numOfInputs, numOfOutputs, pos, plugins=None, defaultBlockId=None):
        if not plugins:
            plugins = []
        self.name = name
        global blockId
        if defaultBlockId is None:
            self.blockId = blockId
            blockId += 1
        else:
            self.blockId = defaultBlockId
        self.numOfInputs = numOfInputs
        self.numOfOutputs = numOfOutputs
        self.plugins = plugins
        self.pos = pos
        self.font = pygame.font.SysFont("timesnewroman", 20, 1)
        self.activeInput = -1
        self.activeOutput = -1
        self.value = None
        self.error = False
        self.numOfInputsX = numOfInputs
        self.numOfOutputsX = numOfOutputs

    def get_width(self):
        label = self.font.render(self.name, 1, (0, 0, 0))
        return 50 * greaterOf(greaterOf(self.numOfInputs, self.numOfOutputs), int(label.get_width() / 50) + 1)

    def display(self, screen):
        for i in range(self.numOfInputs):
            colour = (0, 0, 255)
            if i == self.activeInput:
                colour = (255, 0, 0)
            pygame.draw.rect(screen, colour, Rect(self.pos[0] + 50 * i + 15, self.pos[1], 20, 21), 0)
            pygame.draw.rect(screen, (0, 0, 0), Rect(self.pos[0] + 50 * i + 15, self.pos[1], 20, 21), 2)
        for i in range(self.numOfOutputs):
            colour = (0, 255, 0)
            if i == self.activeOutput:
                colour = (255, 0, 0)
            pygame.draw.rect(screen, colour, Rect(self.pos[0] + 50 * i + 15, self.pos[1] + 69, 20, 21), 0)
            pygame.draw.rect(screen, (0, 0, 0), Rect(self.pos[0] + 50 * i + 15, self.pos[1] + 69, 20, 21), 2)
        colour = (255,255,255)
        if self.error:
            colour = (255,0,0)
        pygame.draw.rect(screen, colour, Rect(self.pos[0], self.pos[1] + 20, self.get_width(), 50), 0)
        pygame.draw.rect(screen, (0, 0, 0), Rect(self.pos[0], self.pos[1] + 20, self.get_width(), 50), 2)
        label = self.font.render(self.name, 1, (0, 0, 0))
        screen.blit(label,
                    [self.pos[0] + (self.get_width() / 2) - (label.get_width() / 2),
                     self.pos[1] + 20 + 25 - (label.get_height() / 2)])

    def get_height(self):
        return 90

    def change_name(self):
        root = tkinter.Tk()
        app = SetName(root, self)
        root.mainloop()
        self.name = app.enteredText.get()


class Link:
    def __init__(self, parent, child, outputNum, inputNum):
        self.parent = parent
        self.child = child
        self.outputNum = outputNum
        self.inputNum = inputNum

    def display(self, screen):
        if type(self.parent) == type(MethodBlock("", 0, 0, [0,0], [0,0])):
            pygame.draw.line(screen, (0, 0, 0),
                            (self.parent.pos[0] + 50 * self.outputNum + 25, self.parent.pos[1]+20),
                            (self.child.pos[0] + 50 * self.inputNum + 25, self.child.pos[1]), 2)
        elif type(self.child) == type(MethodBlock("", 0, 0, [0,0], [0,0])):
            pygame.draw.line(screen, (0, 0, 0),
                            (self.parent.pos[0] + 50 * self.outputNum + 25, self.parent.pos[1] + self.parent.get_height()),
                            (self.child.pos[0] + 50 * self.inputNum + 25, self.child.pos[1] + self.child.get_height()-20), 2)
        elif type(self.parent) == type(MethodBlock("", 0, 0, [0,0], [0,0])) and type(self.child) == type(MethodBlock("", 0, 0, [0,0], [0,0])):
            pygame.draw.line(screen, (0, 0, 0),
                            (self.parent.pos[0] + 50 * self.outputNum + 25, self.parent.pos[1]+20),
                            (self.child.pos[0] + 50 * self.inputNum + 25, self.child.pos[1] + self.child.get_height()-20), 2)
        else:
            pygame.draw.line(screen, (0, 0, 0),
                            (self.parent.pos[0] + 50 * self.outputNum + 25, self.parent.pos[1] + self.parent.get_height()),
                            (self.child.pos[0] + 50 * self.inputNum + 25, self.child.pos[1]), 2)


screen = pygame.display.set_mode((1000, 625), 0, 32)
pygame.display.set_caption("Visual Programming")

blocks = list()
dragging = None
draggingOffset = [0, 0]
draggingOrigin = [0, 0]

links = list()
linkParent = None
linkChild = None
linkParentOutput = -1
linkChildInput = -1

menuPageTitleFont = pygame.font.SysFont("timesnewroman", 20, 1)
menuPageTitles = ["Data",
                  "Input / Output",
                  "Arithmetic",
                  "Data Conversions",
                  "Conditionals 1/3",
                  "Conditionals 2/3",
                  "Conditionals 3/3",
                  "Boolean Operators",
                  "Methods",
                  "System"]

c = Counter()

menuItems = list()
# Data
menuItems.append(MenuItem("variable", 1, 1, c.get(), ["set name", "variable"]))
menuItems.append(MenuItem("Literal", 0, 1, c.get(), ["literal", "set name"]))
menuItems.append(MenuItem("length", 1, 1, c.get()))
menuItems.append(MenuItem("set", 2, 0, c.get()))
menuItems.append(MenuItem("random", 2, 1, c.get()))
# IO
c.new_page()
menuItems.append(MenuItem("print", 1, 0, c.get()))
menuItems.append(MenuItem("input", 1, 1, c.get()))
# Arithmetic
c.new_page()
menuItems.append(MenuItem("add", 2, 1, c.get()))
menuItems.append(MenuItem("subtract", 2, 1, c.get()))
menuItems.append(MenuItem("multiply", 2, 1, c.get()))
menuItems.append(MenuItem("divide", 2, 1, c.get()))
menuItems.append(MenuItem("modulus", 2, 1, c.get()))
# Data Conversion
c.new_page()
menuItems.append(MenuItem("str", 1, 1, c.get()))
menuItems.append(MenuItem("int", 1, 1, c.get()))
menuItems.append(MenuItem("float", 1, 1, c.get()))
menuItems.append(MenuItem("boolean", 1, 1, c.get()))
# Conditionals
c.new_page()
menuItems.append(MenuItem("if", 1, 0, c.get()))
menuItems.append(MenuItem("else", 0, 0, c.get()))
menuItems.append(MenuItem("end", 0, 0, c.get()))
menuItems.append(MenuItem("while", 1, 0, c.get()))
menuItems.append(MenuItem("for", 2, 0, c.get()))
menuItems.append(MenuItem("equal", 2, 1, c.get()))
menuItems.append(MenuItem("not equal", 2, 1, c.get()))
menuItems.append(MenuItem("less than", 2, 1, c.get()))
menuItems.append(MenuItem("less than or equal", 2, 1, c.get()))
menuItems.append(MenuItem("greater than", 2, 1, c.get()))
menuItems.append(MenuItem("greater than or equal", 2, 1, c.get()))
# Boolean Operators
c.new_page()
menuItems.append(MenuItem("and", 2, 1, c.get()))
menuItems.append(MenuItem("or", 2, 1, c.get()))
menuItems.append(MenuItem("not", 1, 1, c.get()))
menuItems.append(MenuItem("nand", 2, 1, c.get()))
menuItems.append(MenuItem("nor", 2, 1, c.get()))
#Methods
c.new_page()
menuItems.append(MenuItem("", 1, 1, c.get(), ["methodblock", "set name"]))
menuItems.append(MenuItem("method", 1, 1, c.get(), ["method", "set name"]))
#System
c.new_page()
menuItems.append(MenuItem("delay", 1, 0, c.get()))

page = 0
start = False
editingOrderMode = False

order = list()

toAddOrder = list()

def getBlockById(blockId, blocks):
    toReturn = None
    for i in blocks:
        if i.blockId == blockId:
            toReturn = i
    return toReturn

for i in read:
    data = i.split(" : ")
    if data[0] == "block":
        generated = Block(data[1], int(data[2]), int(data[3]), [int(x) for x in data[5][1:-1].split(",")],
                          data[4][1:-1].replace("'", "").split(", "), defaultBlockId=int(data[6]))
        if int(data[7]) >= 0:
            toAddOrder.append([generated, int(data[7])])
        blocks.append(generated)
    if data[0] == "literal":
        generated = Literal(data[1], data[2], [int(x) for x in data[3][1:-1].split(",")], defaultBlockId=int(data[4]))
        if int(data[5]) >= 0:
            toAddOrder.append([generated, int(data[5])])
        blocks.append(generated)
    if data[0] == "methodblock":
        generated = MethodBlock(data[1], int(data[2]), int(data[3]), [int(x) for x in data[4][1:-1].split(",")], [int(x) for x in data[5][1:-1].split(",")], plugins=["set name", "methodblock"], defaultBlockId=int(data[6]))
        blocks.append(generated)

for i in read:
    data = i.split(" : ")
    if data[0] == "link":
        parent = getBlockById(int(data[1]), blocks)
        generated = Link(parent, getBlockById(int(data[2]), blocks), int(data[3]), int(data[4]))
        links.append(generated)
    if data[0] == "orderitem":
        getBlockById(int(data[1]), blocks).order.append(getBlockById(int(data[2]), blocks))

changes = -1
while changes != 0:
    changes = 0
    for i in range(len(toAddOrder)-1):
        if toAddOrder[i][1] > toAddOrder[i+1][1]:
            changes += 1
            temp = toAddOrder[i]
            toAddOrder[i] = toAddOrder[i+1]
            toAddOrder[i+1] = temp

for i in range(len(toAddOrder)):
    toAddOrder[i] = toAddOrder[i][0]

order += toAddOrder

for block in blocks:
    if block.blockId > blockId:
        blockId = block.blockId

blockId += 1

while True:
    mousePos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            if mousePos[0] < 750:
                toRemove = list()
                for block in blocks:
                    if block.pos[0] <= mousePos[0] <= block.pos[0] + block.get_width():
                        if block.pos[1] + 20 <= mousePos[1] <= block.pos[1] + 20 + (block.get_height() - 40):
                            if event.button == 1:
                                if type(block) != type(MethodBlock("", 0, 0, [0,0], [0,0])) or dragging is None:
                                    dragging = block
                                    draggingOffset = [mousePos[0] - block.pos[0], mousePos[1] - block.pos[1]]
                                    draggingOrigin = copy.deepcopy(block.pos)
                            else:
                                toRemove.append(block)
                                changes = -1
                                while changes != 0:
                                    changes = 0
                                    for i in links:
                                        if i.parent == block or i.child == block:
                                            links.remove(i)
                                            changes += 1
                                if block in order:
                                    order.remove(block)
                    if block.pos[1] <= mousePos[1] <= block.pos[1] + 20:
                        for currentInput in range(block.numOfInputsX):
                            if block.pos[0] + 50 * currentInput + 15 <= mousePos[0] <= block.pos[
                                0] + 50 * currentInput + 35 and (linkChild is None or type(block) == type(MethodBlock("", 0, 0, [0,0], [0,0]))):
                                found = True
                                for link in links:
                                    if block == link.child and link.inputNum == currentInput and type(block) != type(MethodBlock("", 0, 0, [0,0], [0,0])):
                                        links.remove(link)
                                        found = False
                                        dragging = None
                                        break
                                if found and type(block) != type(MethodBlock("", 0, 0, [0,0], [0,0])):
                                    block.activeInput = currentInput
                                    linkChild = block
                                    linkChildInput = currentInput
                                    dragging = None
                                elif type(block) == type(MethodBlock("", 0, 0, [0,0], [0,0])):
                                    block.activeOutput = currentInput
                                    linkParent = block
                                    linkParentOutput = currentInput
                                    dragging = None
                    if block.pos[1] + block.get_height() - 20 <= mousePos[1] <= block.pos[1] + 40 + block.get_height():
                        for currentOutput in range(block.numOfOutputsX):
                            if block.pos[0] + 50 * currentOutput + 15 <= mousePos[0] <= block.pos[
                                0] + 50 * currentOutput + 35:
                                found = True
                                for link in links:
                                    if block == link.child and link.inputNum == currentOutput and type(block) == type(MethodBlock("", 0, 0, [0,0], [0,0])):
                                        links.remove(link)
                                        found = False
                                        dragging = None
                                        break
                                if type(block) != type(MethodBlock("", 0, 0, [0,0], [0,0])):
                                    block.activeOutput = currentOutput
                                    linkParent = block
                                    linkParentOutput = currentOutput
                                    dragging = None
                                elif found and type(block) == type(MethodBlock("", 0, 0, [0,0], [0,0])):
                                    block.activeInput = currentOutput
                                    linkChild = block
                                    linkChildInput = currentOutput
                                    dragging = None
                if len(toRemove) > 0:
                    blocks.remove(toRemove[-1])
            else:
                for i in menuItems:
                    if 750 + (250 / 2) - i.block.get_width() / 2 <= mousePos[0] <= 750 + (
                                250 / 2) + i.block.get_width() / 2:
                        if 20 + i.pos[1] <= mousePos[1] <= i.pos[1] + i.block.get_height() - 20:
                            if page == i.page:
                                blocks.append(i.get_new())

        if event.type == MOUSEBUTTONUP:
            if dragging is not None:
                if str(draggingOrigin) == str(dragging.pos):
                    if editingOrderMode:
                        inBlock = False
                        for i in blocks:
                            if type(i) == type(MethodBlock("", 0, 0, [0,0], [0,0])):
                                if i.pos[0] <= mousePos[0] <= i.pos[0]+i.get_width():
                                    if i.pos[1]+20 <= mousePos[1] <= i.pos[1]+i.get_height()-20:
                                        inBlock = True
                                        if dragging not in i.order:
                                            i.order.append(dragging)
                                        else:
                                            i.order.remove(dragging)
                        if not inBlock:
                            if dragging not in order:
                                order.append(dragging)
                            else:
                                order.remove(dragging)
                    else:
                        if "set name" in dragging.plugins or type(dragging) == type(
                                Literal("", "", [0, 0])):
                            dragging.change_name()
                dragging = None
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if linkChild is not None:
                    linkChild.activeInput = -1
                    linkChild = None
                elif linkParent is not None:
                    linkParent.activeOutput = -1
                    linkParent = None
                else:
                    rootEx = tkinter.Tk()
                    root = rootEx.withdraw()
                    f = filedialog.asksaveasfile(mode='w', defaultextension=".jpp")
                    if f is not None:
                        textToWrite = ""
                        for i in copy.copy(blocks):
                            positionInOrder = -1
                            if i in order:
                                positionInOrder = order.index(i)
                            if type(i) == type(Literal("", "", [0, 0])):
                                textToWrite += " : ".join(str(x) for x in ["literal",
                                                                           i.dataType,
                                                                           i.value,
                                                                           i.pos,
                                                                           i.blockId,
                                                                           positionInOrder]) + "\n"
                            elif type(i) == type(MethodBlock("", 0, 0, [0,0], [0,0])):
                                textToWrite += " : ".join(str(x) for x in ["methodblock",
                                                                           i.name,
                                                                           i.numOfInputs,
                                                                           i.numOfOutputs,
                                                                           i.pos,
                                                                           i.size,
                                                                           i.blockId]) + "\n"
                            else:
                                textToWrite += " : ".join(str(x) for x in ["block",
                                                                           i.name,
                                                                           i.numOfInputs,
                                                                           i.numOfOutputs,
                                                                           i.plugins,
                                                                           i.pos,
                                                                           i.blockId,
                                                                           positionInOrder]) + "\n"
                        for i in copy.copy(links):
                            textToWrite += " : ".join(str(x) for x in ["link",
                                                                       i.parent.blockId,
                                                                       i.child.blockId,
                                                                       i.outputNum,
                                                                       i.inputNum]) + "\n"
                        for i in [j for j in copy.copy(blocks) if type(j) == type(MethodBlock("",0,0,[0,0],[0,0]))]:
                            for j in i.order:
                                textToWrite += " : ".join(str(x) for x in ["orderitem",
                                                                           i.blockId,
                                                                           j.blockId]) + "\n"
                        f.write(textToWrite)
                        f.close()
                    rootEx.destroy()
            if mousePos[0] >= 750:
                if event.key == K_LEFT:
                    if page > 0:
                        page -= 1
                if event.key == K_RIGHT:
                    if page < menuItems[-1].page:
                        page += 1
            if event.key == K_RETURN:
                start = True
                for i in blocks:
                    i.error = False
            if event.key == K_TAB:
                editingOrderMode = editingOrderMode == False
            if editingOrderMode:
                for block in blocks:
                    if block.pos[0] <= mousePos[0] <= block.pos[0] + block.get_width():
                        if block.pos[1] + 20 <= mousePos[1] <= block.pos[1] + 20 + (block.get_height() - 40):
                            if block in order and len(order) > 1:
                                if event.key == K_LEFT:
                                    if order.index(block) > 0:
                                        blockIndex = order.index(block)
                                        order[blockIndex] = order[blockIndex - 1]
                                        order[blockIndex - 1] = block
                                if event.key == K_RIGHT:
                                    if order.index(block) < len(order) - 1:
                                        blockIndex = order.index(block)
                                        order[blockIndex] = order[blockIndex + 1]
                                        order[blockIndex + 1] = block

    screen.fill((255, 255, 255))

    keys = pygame.key.get_pressed()
    if not editingOrderMode and mousePos[0] < 750:
        xOffset = 0
        yOffset = 0
        if keys[K_LEFT]:
            for i in blocks:
                if "methodblock" in i.plugins:
                    if i.pos[0] <= mousePos[0] <= i.pos[0]+i.get_width():
                        if i.pos[1] <= mousePos[1] <= i.pos[1]+i.get_height():
                            if keys[K_LSHIFT]:
                                i.size[0] -= 2
            if not keys[K_LSHIFT]:
                xOffset = 2
        if keys[K_RIGHT]:
            for i in blocks:
                if "methodblock" in i.plugins:
                    if i.pos[0] <= mousePos[0] <= i.pos[0]+i.get_width():
                        if i.pos[1] <= mousePos[1] <= i.pos[1]+i.get_height():
                            if keys[K_LSHIFT]:
                                i.size[0] += 2
            if not keys[K_LSHIFT]:
                xOffset = -2
        if keys[K_UP]:
            for i in blocks:
                if "methodblock" in i.plugins:
                    if i.pos[0] <= mousePos[0] <= i.pos[0]+i.get_width():
                        if i.pos[1] <= mousePos[1] <= i.pos[1]+i.get_height():
                            if keys[K_LSHIFT]:
                                i.size[1] -= 2
            if not keys[K_LSHIFT]:
                yOffset = 2
        if keys[K_DOWN]:
            for i in blocks:
                if "methodblock" in i.plugins:
                    if i.pos[0] <= mousePos[0] <= i.pos[0]+i.get_width():
                        if i.pos[1] <= mousePos[1] <= i.pos[1]+i.get_height():
                            if keys[K_LSHIFT]:
                                i.size[1] += 2
            if not keys[K_LSHIFT]:
                yOffset = -2
        for block in blocks:
            block.pos[0] += xOffset*len(blocks)
            block.pos[1] += yOffset*len(blocks)


    for i in [order] + [block.order for block in blocks if type(block) == type(MethodBlock("", 0, 0, [0,0], [0,0]))]:
        if len(i) > 0:
            pygame.draw.line(screen, (255, 0, 0), [i[0].pos[0] - 50, i[0].pos[1] + i[0].get_height() / 2],
                             [i[0].pos[0], i[0].pos[1] + i[0].get_height() / 2], 5)
        for j in range(len(i) - 1):
            pygame.draw.line(screen, (255, 0, 0),
                             [i[j].pos[0] + i[j].get_width(), i[j].pos[1] + i[j].get_height() / 2],
                             [i[j + 1].pos[0],
                              i[j + 1].pos[1] + i[j + 1].get_height() / 2], 5)

    for i in blocks + links:
        i.display(screen)

    if start:
        label = menuPageTitleFont.render("Running", 1, (255, 0, 0))
        screen.blit(label, (5, 5))

    if start:
        skip = False
        skipElse = False
        skipWhile = False
        forBlock = None
        numOfIfs = 0
        numOfEnds = 0
        numOfElses = 0
        blockToReturn = -1
        for block in blocks:
            if "variable" in block.plugins:
                block.value = None
        blockIndex = 0
        while blockIndex < len(order):
            pygame.display.update()
            toBreak = False
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        toBreak = True
            if toBreak:
                break
            block = order[blockIndex]
            if skip or skipElse or skipWhile:
                if block.name in ["if", "while", "for"]:
                    numOfIfs += 1
                elif block.name == "end":
                    numOfEnds += 1
                    if numOfEnds == numOfIfs:
                        skip = False
                        skipElse = False
                        skipWhile = False
                        foring = False
                elif block.name == "else" and skipElse == False and skipWhile == False:
                    numOfElses += 1
                    if numOfElses == numOfIfs:
                        skip = False
                        numOfElses -= 1
                blockIndex += 1
                continue
            successful = run(block, links, blocks)
            if len(successful) > 0:
                successful = successful[0]
            if block.name == "end":
                numOfEnds += 1
                if numOfEnds != numOfIfs:
                    if blockToReturn != -1:
                        blockIndex = blockToReturn
                        blockToReturn = -1
                        if forBlock is not None:
                            for link in links:
                                if link.child == forBlock:
                                    if link.inputNum == 0:
                                        link.parent.value = int(link.parent.value)+1
                    else:
                        blockIndex += 1
                else:
                    blockIndex += 1
                continue
            if block.name == "if":
                if not successful:
                    skip = True
                    numOfIfs = 1
                    numOfEnds = 0
                    numOfElses = 0
            if block.name == "else":
                skipElse = True
                numOfIfs = 1
                numOfEnds = 0
            if block.name == "while" or block.name == "for":
                if not successful:
                    skipWhile = True
                    numOfIfs = 1
                    numOfEnds = 0
                else:
                    blockToReturn = blockIndex
                    if block.name == "for":
                        forBlock = block
            blockIndex += 1
        start = False

    if dragging is not None and mousePos[0] < 750:
        dragging.pos = [mousePos[0] - draggingOffset[0], mousePos[1] - draggingOffset[1]]

    if linkParent is not None and linkChild is not None:
        links.append(Link(linkParent, linkChild, linkParentOutput, linkChildInput))
        linkParent.activeOutput = -1
        linkChild.activeInput = -1
        linkParent = None
        linkChild = None

    pygame.draw.rect(screen, (255, 255, 255), Rect(750, 0, 250, 625), 0)
    pygame.draw.line(screen, (0, 0, 0), (750, 0), (750, 625), 2)

    label = menuPageTitleFont.render(menuPageTitles[page], 1, (0, 0, 0))
    screen.blit(label, [750 + (250 / 2) - label.get_width() / 2, 15])

    if editingOrderMode:
        label = menuPageTitleFont.render("Edit Command Runtime Order", 1, (255, 0, 0))
        screen.blit(label, (5, 5))

    for i in menuItems:
        if i.page == page:
            i.display(screen)

    pygame.display.update()
