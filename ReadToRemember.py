# Read to Remember

"""
В системе 3 основных действия:
    1 Добавить новый прочтенный материал: ссылка, текст, документ
    2 Получить список того, что на сегодняшний день нужно повторить
    3 Отметить что повторил

Система будет составлять список для повторения на день, согласно кривой обучения
Если одна из задач не будет выполнена, можно корректировать даты повторов,
добавлять и убирать новые повторения.

Добавить:
    Кнопка "Запомнил"
    Тесты на запомненное
    Градиент того на сколько хорошо запомнил
    Систему фильтров задач
    Система приоритезации
    Система категоризации
    Спец интерфейс для указания глав книг
    Специальная кривая обучения для больших источников, как книга
    Для каждого таска добавить:
        - подразделы для отдельных глав или сегоментов
        - категория материала, область знаний
    Добавить функционал "Помидоро" 25мин чтения, 5 мин отдыха
    Когда нагрзка падает ниже уровня Х, добавить таск "Пора изучить что-нибудь новенькое"
        Можно предложить тему на основе популярности категории или качества запоминания
    В случаях высокой нагрузки сдвигать часть тасков на поздних этапах
    Добавить объем источника:
        - время видео
        - время затраченное на первое прочтение
        - количество символов / страниц
        - выводить из этого оценку затраченного времени

    Таск состоящий из набора флеш-карт


По собранной статистики выводить персонализированную кривую обучения.

"""
#from appJar import gui
import threading
from datetime import datetime
from datetime import timedelta
import json
import os
import pprint
pp = pprint.PrettyPrinter(indent=2)

def log(text,lvl=0,indent=0):
    line_start = str(get_dttm()) + "\t" * indent
    if type(text) == list:
        str_text = ""
        for el in text:
            str_text = str_text + " " + str(el)
        print(line_start,str_text)
    elif type(text) == dict:
        print(line_start)
        pp.pprint(dict_el_to_str(text))
    else:
        print(line_start,text)
    return False

#################### Time Functions ####################
def get_date():
    return datetime.date(datetime.now())

def get_dttm():
    return datetime.now()

def add_days(date,days_num):
    return date + timedelta(days=days_num)

def days_diff(d1,d2):
    dif = d2 - d1
    return dif.days

def add_seconds(dttm,sec):
    return dttm + timedelta(seconds=sec)

def seconds_diff(t1,t2):
    dif = t1 - t2
    return dif.total_seconds()

def time_functions_test():
    test_result = True
    date1 = get_date()
    if not date1:
        log("Failed get_date()",indent=1)
        test_result = False
    date2 = add_days(date1,3)
    if not days_diff(date1,date2) == 3:
        log("Failed add_days() or days_diff()",indent=1)
        test_result = False
    dttm1 = get_dttm()
    if not date1:
        log("Failed get_dttm()",indent=1)
        test_result = False
    dttm2 = add_seconds(dttm1,3)
    if not seconds_diff(dttm1,dttm2) == -3:
        log("Failed add_seconds() or seconds_diff()",indent=1)
        test_result = False
    return test_result

#################### Parameters and GV ####################
study_list = dict()# Содержит библиотеку материалов для запоминания
normal_tasks_for_today = list() # Task_id
overdue_tasks = list() # Task_id

all_tasks = list() # Task_id
meta_file = dict()
list_of_tasks = {} # Collection of tasks objects for runtime

curr_date = get_date()
curr_dttm = get_dttm()

# Meta Template
meta_template = {
      'tasks':{
              0:{#Task_id
                'name':'Welcom to ReadToRemeber!',
                'type':'',
                'body':'',
                'status':'New',
                'priority':0,
                'create_dttm':curr_dttm,
                'current_curve_stage':0,
                'last_repeat_date':curr_date,
                'next_repeat_date':curr_date,
                'update_dttm':''
              }},
      'update_dttm':curr_dttm
}

meta_file_path = os.environ['APPDATA'] + '\\HandyApps\\RtR_Data\\meta.json'
test_dir_path = os.environ['APPDATA'] + '\\HandyApps\\Test\\file_manager_test.json'
params = {
        'lib_path':'',
        #'meta_file_path':'D:\\Projects\\HandyApps\\RtR_Data\\meta.json',
        'meta_file_path':meta_file_path,
        #'test_dir_path':'D:\\Projects\\HandyApps\\Test\\file_manager_test.json',
        'test_dir_path':test_dir_path,
        'docs_folder':''
        }

learning_curve = {
        # Number of days before need to repeat
        # Добавить кастомные формулы типа {'x*2':[0,1]}
        #  где x это предыдущее значение дней, а [0,1] - первые n значений
        #  пример 1: {'x*2':[0,1]} = [0,1,2,4,8,16...]
        #  пример 2: {'x':[1]} = [1,1,1,1...]
        #  пример 3: {'(x+1)^2':[0,1]} = [0,1,4,25,26^2...]
        #  пример 4: {'x':[2,5,10,19,432]} = [2,5,10,19,432...]
        1:0,
        2:1,
        3:7,
        4:28,
        5:84,
        6:336
        }

#################### Metadata Manager ####################
class Meta():
    """
    Holds methods related to processing metadata
    Meta holds data on:
        - App logs and history
        - Task data, except attached files
    """
    def add_task(task_content,priority=1,task_id=None):
        """
        Add task
        """        
        global meta_file
        if task_id==None:
            if len(list(meta_file['tasks'].keys())) > 0:
                task_id = list(meta_file['tasks'].keys())[-1] + 1
            else:
                task_id = 0

        task = dict(Task.task_template)
        task['name'] = task_content['name']
        task['type'] = task_content['type']
        task['body'] = task_content['body']
        task['status'] = task_content['status']
        task['priority'] = task_content['priority']
        task['create_dttm'] = get_dttm()
        task['current_curve_stage'] = 0
        task['last_repeat_date'] = None
        task['next_repeat_date'] = None #task_content['next_repeat_date']
        task['update_dttm'] = get_dttm()

        meta_file['tasks'][task_id] = task
        normal_tasks_for_today.append(task_id)
        return True

    def remove_task(task_id):
        """
        Delete task
        """
        meta_file.pop(task_id, None)
        return True

    def read_meta_file():
        """
        Read metadata from json file on disc.
        """
        global meta_file
        global normal_tasks_for_today
        global overdued_tasks
        global all_tasks
        meta_file = read_json_to_dict(params['meta_file_path'])
        if meta_file=={}:
            log("Metadata could not be read. Creating new metadata file " + params['meta_file_path'])
            global meta_template
            meta_file = dict(meta_template)

        today = get_date()

        # Зачитать таски, проапдейтить статусы
        for task_id, task in meta_file['tasks'].items():
            meta_file['tasks'][task_id] = Task.refresh_statuses(task)
            next_repeat_date = task['next_repeat_date']
            
            all_tasks.append(task_id)
            
            if days_diff(next_repeat_date, today) == 0:
                # Doing today
                normal_tasks_for_today.append(task_id)
            elif days_diff(next_repeat_date, today) < 0:
                # Overdued
                overdued_tasks.append(task_id)
            else:
                # Doing not today
                pass

        """
        lcs = learning_curve[task_content['current_curve_stage']] # Learning Curve Stage
        if ((task_content['next_repeat_date'] < today
             and add_days(task_content['last_repeat_date'],lcs) == today)
            or task.next_repeat_date == today):
            # Делаем сегодня
            task.next_repeat_date = today
            task.update_dttm = today_dttm # Вынести в отдельную функцию все апдейты?
            normal_tasks_for_today.append(task)
            pass
        elif task_content['next_repeat_date'] < today and add_days(task_content['last_repeat_date'],lcs) < today:
            # Опоздал, штрафная
            overdue_tasks.append(task_id)
            task.mark_as_read(task_id)
        else:
            # Время еще не пришло
            pass
        all_tasks.append(task_id)
        """
        return True

    def write_meta():
        """
        Dump metadata on disc as json.
        """
        global meta_file
        write_dict_to_json(params['meta_file_path'],meta_file)
        return True

def metadata_test():
    test_result = True
    test_task_id = -1

    add_task = Meta.add_task(dict(Task.task_template),task_id=test_task_id)
    if not add_task:
        log("Failed Meta.add_task()",indent=1)
        test_result = False

    remove_task = Meta.remove_task(test_task_id)
    if not remove_task:
        log("Failed Meta.remove_task()",indent=1)
        test_result = False

    return test_result

#################### Task Manager ####################
class Task():
    """
    Holds methods related to managing tasks.
    Decided not to implement Task as objects, but to process as dicts.
        This way it will require less processing and should be faster.
    """
    task_template = {
      'name':'', #str
      'type':'', # Text / File / Link
      'body':'', #?
      'status':'New', #str
      'priority':0, #num
      'create_dttm':'', #dttm
      'current_curve_stage':0, #num
      'last_repeat_date':'', #date
      'next_repeat_date':'', #date
      'update_dttm':'' #dttm
      }

    def create_task(task_data,priority=1):
        """
        Добавить задачу в список

        Таск добавляется наподобие того как реализовано в Wunderlist:
            - Введенный текст становится заголовком
            - Внутри таска можно добавлять файлы, подзадачи и т.п.
        При добавлении таска "как файла", название файла
            становится заголовком таска (корректируемый).

        """
        def get_task_body(t):
            return (None,None)

        def get_task_header(t):
            """
            Determines name of the task
            """
            pass

        today = get_date()
        today_dttm = get_dttm()
        task_header = get_task_header(task_data)
        (task_body, task_type) = get_task_body(task_data)

        # Task Template
        task = dict(Task.task_template)
        task['name'] = task_header
        task['type'] = task_type # Text / File / Link
        task['body'] = task_body
        task['status'] = 'New'
        task['priority'] = priority
        task['create_dttm'] = today_dttm
        task['current_curve_stage'] = 1
        task['last_repeat_date'] = today
        task['next_repeat_date'] = today
        task['update_dttm'] = today_dttm

        return task

    def mark_as_read(task):
        """
        Mark task as recently read.
        """
        task['status'] = 'Read'
        task['last_repeat_date'] = get_date()
        task['current_curve_stage'] = task['current_curve_stage'] + 1
        task['next_repeat_date'] = Task.calc_next_repeat_date(task)
        return Task.refresh_statuses(task)

    def mark_as_overdue(task):
        """
        Mark task as overdued
        """
        task['status'] = 'Overdue'
        return Task.refresh_statuses(task)
        
    def mark_as_complete(task):
        """
        Mark task as complete. Material is learned.
        """
        task['status'] = 'Complete'
        return Task.refresh_statuses(task)
        
    def mark_as_canceled(task):
        """
        Mark task as cancelled. Task will no longer be processed.
        """
        task['status'] = 'Cancelled'
        return Task.refresh_statuses(task)

    def mark_as_new(task):
        """
        Mark task as new. Restart learning process.
        """
        task['status'] = 'New'
        task['last_repeat_date'] = get_date()
        task['current_curve_stage'] = 1
        task['next_repeat_date'] = Task.calc_next_repeat_date(task)
        return Task.refresh_statuses(task)

    def delay_task(task,days):
        """
        Delay task for specified number of days
        """
        task['status'] = 'Delayed'
        task['next_repeat_date'] = add_days(get_date(), days)
        return Task.refresh_statuses(task)

    def calc_next_repeat_date(task):
        """
        Calculates next repeat date.
        """
        days_till_next_time = learning_curve[task['current_curve_stage']]
        return add_days(task['last_repeat_date'],days_till_next_time)

    def refresh_statuses(task):
        """
        Refresh:
            - Current status
            - Dates
            - Penalties
            - Learning curve status
        """
        task['update_dttm'] = get_dttm()
        return task

def task_test():
    task = dict(Task.task_template)
    test_result = True

    task = Task.mark_as_read(task)
    if task['status'] != 'Read':
        log("Failed Task.mark_as_read()",indent=1)
        test_result = False

    task = Task.mark_as_overdue(task)
    if task['status'] != 'Overdue':
        log("Failed Task.mark_as_overdue()",indent=1)
        test_result = False

    task = Task.mark_as_complete(task)
    if task['status'] != 'Complete':
        log("Failed Task.mark_as_complete()",indent=1)
        test_result = False

    task = Task.mark_as_canceled(task)
    if task['status'] != 'Cancelled':
        log("Failed Task.mark_as_canceled()",indent=1)
        test_result = False

    task = Task.delay_task(task,3)
    if task['status'] != 'Delayed':
        log("Failed Task.delay_task()",indent=1)
        test_result = False

    task = Task.mark_as_new(task)
    if task['status'] != 'New':
        log("Failed Task.mark_as_new()",indent=1)
        test_result = False

    task = Task.refresh_statuses(task)
    if task['update_dttm'] != get_dttm():
        log("Failed Task.refresh_statuses()",indent=1)
        test_result = False

    return test_result


#################### Converters ####################
def dict_el_to_str(d):
    """
    Convert dict elems of known class types to string
        and returns converted dict.
    Known types:
        - date
        - dttm
    """
    date_type = get_date()
    dttm_type = get_dttm()
    for k,v in d.items():
        if type(v) == dict:
            d[k] = dict_el_to_str(v)
        elif (type(v) is type(date_type)
            or type(v) is type(dttm_type)):
            d[k] = str(v)
    return d

#################### File Manager ####################
def read_json_to_dict(path):
    data = {}
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
    else:
        log("File " + path + " not found.")
        return {}
    return data

def write_dict_to_json(path,data_dict):
    """
    Writes dict to file on disk.
    """
    # Make dir first
    if not os.path.exists(path[0:path.rfind("\\")]):
        os.makedirs(path[0:path.rfind("\\")])

    with open(path, 'w') as f:
        json.dump(dict_el_to_str(data_dict), f, ensure_ascii=False)
    return True

def file_manager_test():
    path = params['test_dir_path']
    data = {
            "feature1":"Value1",
            "feature2":2,
            "feature3":["Value3","Value4"],
            "feature4":{
                    "feature5":"Value5",
                    "feature6":curr_dttm
                    }
            }
    write_dict_to_json(path,data)
    control_data = read_json_to_dict(path)
    os.remove(path)
    os.rmdir(path[0:path.rfind("\\")])
    
    if control_data==dict_el_to_str(data):
        return True
    else:
        return False

#################### GUI Manager ####################
def press(button):
    global app
    if button == "Add":
        new_task = app.getEntry("New Task")
        if new_task == '':
            app.popUp("Task is not specified",)
        log("New task:" + new_task)
    else:
        pass
    return False

#with gui("Study Materials", "400x200", font={'size':18}) as app:
#    app.addLabel("title", "Plan for today:")
#    app.addLabelEntry("New Task")
#    app.addButtons(["Add"], press)

#################### Runtime Manager ####################

def startup():
    """
    Подготовка данных к работе приложения
    Зачитывание метаданных
    """
    meta_read_successful = Meta.read_meta_file()
    if not meta_read_successful:
        return False
    # Start_GUI() - to be added
    return True
# Execution
startup()
log("App is running.")

log("Current metadata state:")
pp.pprint(dict_el_to_str(meta_file))

cycle_cnt = 0
def check_status():
    global cycle_cnt
    if cycle_cnt > 10:
        log("Finishing app")
        return False
    else:
        threading.Timer(5, check_status).start()
        cycle_cnt += 1
        log("Cycle" + str(cycle_cnt))
    # Add whatever should be inside the cycle.

#check_status()

#################### Test Manager ####################
def test_manager():
    log("Starting test.")
    if file_manager_test():
        pass
    else:
        log("!!! File Manager test is FAILED!")

    if task_test():
        pass
    else:
        log("!!! Task test is FAILED!")

    if metadata_test():
        pass
    else:
        log("!!! Metadata test is FAILED!")

    if time_functions_test():
        pass
    else:
        log("!!! Time Functions test is FAILED!")
    log("Tests finished.")
    return True

test_manager()

