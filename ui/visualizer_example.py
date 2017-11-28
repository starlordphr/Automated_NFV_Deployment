import random, time
import visualizer

data = []
SAMPLE_SIZE = 50

def gen_next_data():
	global data
	data.append(random.random() * 20 + 5)
	if len(data) > SAMPLE_SIZE:
		data = data[1:]

def main():
	gen_next_data()
	gen_next_data()

	visualizer.open_window(x_size=SAMPLE_SIZE)

	while True:
		time.sleep(0.2)
		gen_next_data()
		visualizer.update_plot(data)

if __name__ == '__main__':
	main()
