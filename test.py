import curses_input

#print(curses_input.select(['thing1', 'thing2'], title="title"))
input_1 = curses_input.string_input(title='Thing1')
input_2 = curses_input.string_input(title='Thing2')

print input_1
print input_2

