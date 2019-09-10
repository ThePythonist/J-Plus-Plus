# J-Plus-Plus

A visual programming language designed to teach an intuitive understanding of programming concepts

## Usage
To run the interpreter, call
```
python3 main.py
```

From there, press "New" to create a new program or "Open" to load an existing program from a ".jpp" file.

If your mouse is in the left-hand region of the window, the arrow keys navigate around the program.

If your mouse is in the right-hand region of the window, the arrow keys will scroll through the block menus.

Clicking on one of the elements in the right-hand menu will add a code block into your program. Most of these blocks have inputs and outputs. Click on the output of one block and then the input of another block to connect them.

Right clicking a box will remove it from the program, and dragging and dropping a block will move it around the program.

To make a runtime order (the order in which the blocks will run), press tab on the keyboard and click the blocks in the order in which you want them to run. With your mouse over a block, the arrow keys will shift its position in the runtime order. Tab again will exit this mode. The blocks will trace the links upwards to find the values to use, so only blocks with no outputs really need to be in the runtime order.

The "str", "int", "float", and "boolean" blocks will convert their inputs into their datatype.

"If" and "While" blocks require a boolean as their input and also require an "end" block (or an optional "else" block in the case of an "if" statement).

The "for" block requires a variable as input 1 and a boolean for input 2. It will loop the code between it and its end block, incrementing the variable of its 1st input each time, until the second input is false.

You can also create your own methods by clicking the white block in the last menu. You can resize these by placing your mouse over them, holding shift and pressing the arrow keys. You can place other blocks inside them and link them to the method's inputs and outputs. You can also create a runtime order for each method in the normal way. The output will only be taken once the runtime order is at the end. These methods can be called using the "method" block.

To save the code press escape, and to run the code press enter and it will run in the normal python console.
