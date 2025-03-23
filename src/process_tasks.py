from task_processor import TaskProcessor

def main():
    try:
        processor = TaskProcessor()
        processor.process_tasks()
    except Exception as e:
        print(f"Error processing tasks: {str(e)}")

if __name__ == "__main__":
    main() 