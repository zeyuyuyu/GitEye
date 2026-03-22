import threading

class MultiThreadedProcessor:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.threads = []

    def process(self, tasks):
        for task in tasks:
            thread = threading.Thread(target=self.execute_task, args=(task,))
            self.threads.append(thread)
            thread.start()

        for thread in self.threads:
            thread.join()

    def execute_task(self, task):
        # Implement your task processing logic here
        print(f"Processing task: {task}")

if __name__ == "__main__":
    processor = MultiThreadedProcessor(num_threads=4)
    tasks = ["task1", "task2", "task3", "task4", "task5", "task6", "task7", "task8"]
    processor.process(tasks)