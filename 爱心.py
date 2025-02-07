import turtle

colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']

t = turtle.Turtle()
t.speed(0)
t.hideturtle()

for y in range(15, -15, -1):
	t.penup()
	t.goto(-300, y * 10)
	t.pendown()
	for x in range(-30, 30):
		if ((x * 0.05) ** 2 + (y * 0.1) ** 2 - 1) ** 3 - (x * 0.05) ** 2 * (y * 0.1) ** 3 <= 0:
			t.pencolor(colors[(x + y) % len(colors)])
			t.forward(10)
		else:
			t.pencolor('white')
			t.forward(10)

turtle.done()
