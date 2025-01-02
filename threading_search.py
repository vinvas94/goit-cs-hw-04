import multiprocessing
import logging
import time
from collections import defaultdict

def search_in_files(file_list, keywords, results):
    logging.info(f"Process {multiprocessing.current_process().name} searching in: {file_list}")
    local_results = defaultdict(list)
    
    for file in file_list:
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    for keyword in keywords:
                        if keyword in line:
                            local_results[keyword].append(file)
        except FileNotFoundError:
            logging.warning(f"File not found: {file}")
        except Exception as e:
            logging.error(f"Error processing file {file}: {e}")

    # Update shared results dictionary
    with results.get_lock():
        for keyword, files in local_results.items():
            if keyword not in results:
                results[keyword] = []
            results[keyword].extend(files)

def multiprocess_search(files, keywords, num_processes=4):
    if not files or not keywords:
        return {}

    logging.basicConfig(level=logging.INFO, format="%(processName)s: %(message)s")
    manager = multiprocessing.Manager()
    results = manager.dict()
    processes = []
    

    files_per_process = len(files) // num_processes + (len(files) % num_processes > 0)

    for i in range(num_processes):
        start_index = i * files_per_process
        end_index = min((i + 1) * files_per_process, len(files))
        process_files = files[start_index:end_index]
        process = multiprocessing.Process(target=search_in_files, args=(process_files, keywords, results))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

  
    return dict(results)


if __name__ == "__main__":
    files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt", "file6.txt"]
    keywords = ["python", "javascript", "<html>"]
    num_processes = 4

    start_time = time.time()
    results = multiprocess_search(files, keywords, num_processes)
    end_time = time.time()

    print(f"Results: {results}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
