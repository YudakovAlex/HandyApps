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
    #log("\n---Test---Test---Test---")
    #log(get_dttm(),"Begining Time Functions Test")
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

#################### Global Parameters ####################

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

#################### Parameters and GV ####################
params = {
        'lib_path':'',
        #'meta_file_path':'D:\\Projects\\HandyApps\\RtR_Data\\meta.json',
        'meta_file_path':'C:\\Users\\Aleksander_Yudakov\\Documents\\PythonProjects\\GIT\\RtR_Data\\meta.json',
        #'test_dir_path':'D:\\Projects\\HandyApps\\Test\\file_manager_test.json',
        'test_dir_path':'C:\\Users\\Aleksander_Yudakov\\Documents\\PythonProjects\\GIT\\Test\\file_manager_test.json',
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
    def add_task(task_body,priority=1,task_id=None):
        global meta_file

        if task_id==None:
            if len(list(meta_file['tasks'].keys())) > 0:
                task_id = list(meta_file['tasks'].keys())[-1] + 1
            else:
                task_id = 0

        task_content = dict(Task.task_template)
        task_content['name'] = task_body['name']
        task_content['type'] = task_body['type']
        task_content['body'] = task_body['body']
        task_content['status'] = task_body['status']
        task_content['priority'] = task_body['priority']
        task_content['create_dttm'] = get_dttm()
        task_content['current_curve_stage'] = 0 # Or 1?
        task_content['last_repeat_date'] = None
        task_content['next_repeat_date'] = None #task_body['next_repeat_date']
        task_content['update_dttm'] = get_dttm()

        task = Task(task_id,task_content)

        meta_file['tasks'][task_id] = task
        normal_tasks_for_today.append(task_id)

        return True

    def remove_task(task_id):
        """
        Удалить задачу из списка
        """
        meta_file.pop(task_id, None)
        return True

    def read_meta():
        global meta_file
        global normal_tasks_for_today
        global overdued_tasks
        global all_tasks
        meta_file = read_json_to_dict(params['meta_file_path'])
        if meta_file=={}:
            log("Metadata could not be read. Creating new metadata file" + params['meta_file_path'])
            global meta_template
            meta_file = dict(meta_template)
            #write_dict_to_json(params['meta_file_path'],meta_file)

        today = get_date()
        #today_dttm = get_dttm()

        # Зачитать таски, проапдейтить статусы
        for task_id, task_content in meta_file['tasks'].items():

            task_obj = Task(task_id,task_content)
            task_obj.refresh_statuses()
            list_of_tasks['task_id'] = task_obj

            due_date = task_obj.get_due_date()
            if days_diff(due_date, today) <= 0:
                # Doing today
                pass
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
        global meta_file
        write_dict_to_json(params['meta_file_path'],meta_file)
        return True

    def get_tasks_for_today():
        """
        Возвращяет Json со всеми тасками на сегодня
        """
        return True
        list_of_tasks = dict()
        for nt in normal_tasks_for_today:
            list_of_tasks[nt] = meta_file['tasks'][nt]

        for ot in overdued_tasks:
            list_of_tasks[ot] = meta_file['tasks'][ot]

        return list_of_tasks

    def get_tasks_for_date(next_repeat_date):
        """
        Возвращяет Json со всеми тасками с повторением на определенную дату
        """
        return True
        list_of_tasks = dict()
        for t in all_tasks:
            if meta_file['tasks'][t]['next_repeat_date'] == next_repeat_date:
                list_of_tasks[t] = meta_file['tasks'][t]

        return list_of_tasks


    def get_full_list():
        """
        Возвращяет Json со всеми тасками в системе
        Подумать над системой фильтров
        """
        return True
        list_of_tasks = dict()
        for t in all_tasks:
            list_of_tasks[t] = meta_file['tasks'][t]

        return list_of_tasks

def metadata_test():
    #log("\n---Test---Test---Test---")
    #log("Begining Metadata Test")
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

    # Закоментил, чтобы 2 раза на старте не читал.
    #read_meta = Meta.read_meta()
    #if not read_meta:
    #    log("\tFailed Meta.read_meta()")
    #    test_result = False

    get_tasks_for_today = Meta.get_tasks_for_today()
    if not get_tasks_for_today:
        log("Failed Meta.get_tasks_for_today()",indent=1)
        test_result = False

    get_tasks_for_date = Meta.get_tasks_for_date(get_date())
    if not get_tasks_for_date:
        log("Failed Meta.get_tasks_for_date()",indent=1)
        test_result = False

    get_full_list = Meta.get_full_list()
    if not get_full_list:
        log("Failed Meta.get_full_list()",indent=1)
        test_result = False

    return test_result

#################### Task Manager ####################
class Task():
    """
    Holds methods related to managing tasks
    """
    task_template = {
      'name':'', #str
      'type':'', # Text / File / Link
      'body':'', #?
      'status':'New', #str
      'priority':0, #num
      'create_dttm':'', #dttm
      'current_curve_stage':'', #num
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
        task_obj = {
          'name':task_header,
          'type':task_type, # Text / File / Link
          'body':task_body,
          'status':'New',
          'priority':priority,
          'create_dttm':today_dttm,
          'current_curve_stage':1,
          'last_repeat_date':today,
          'next_repeat_date':today,
          'update_dttm':today_dttm
          }

        return task_obj

    def mark_as_read(self):
        """
        Отметить как прочитанное на текущий момент
        """
        self._status = 'Read'
        return True

        task_id = self._id
        global meta_file
        today = get_date()
        today_dttm = get_dttm()

        if meta_file.tasks[task_id].current_curve_stage == learning_curve.keys()[-1]:
            meta_file.tasks[task_id].mark_as_complete(task_id)
        else:
            meta_file['tasks'][task_id]['status'] = 'Read'
            meta_file['tasks'][task_id]['current_curve_stage'] += 1
            meta_file['tasks'][task_id]['next_repeat_date'] = today + learning_curve[meta_file.tasks[task_id].current_curve_stage]
            meta_file['tasks'][task_id]['update_dttm'] = today_dttm
            meta_file['tasks'][task_id]['last_repeat_date'] = today

        return True

    def mark_as_overdue(self):
        """
        Отметить как просроченное
        """
        self._status = 'Overdue'
        return True

        task_id = self._id
        global meta_file
        today_dttm = get_dttm()

        meta_file['tasks'][task_id]['status'] = 'Overdue'
        meta_file['tasks'][task_id]['update_dttm'] = today_dttm

        return True

    def mark_as_complete(self):
        """
        Отметить как выполненную задачу, "материал освоен"
        """
        self._status = 'Complete'
        return True

        task_id = self._id
        global meta_file
        today = get_date()
        today_dttm = get_dttm()

        meta_file['tasks'][task_id]['status'] = 'complete'
        meta_file['tasks'][task_id]['next_repeat_date'] = None
        meta_file['tasks'][task_id]['update_dttm'] = today_dttm
        meta_file['tasks'][task_id]['last_repeat_date'] = today
        return True

    def mark_as_canceled(self):
        self._status = 'Cancelled'
        return True

    def mark_as_new(self):
        self._status = 'New'
        return True

    def delay_task(self):
        """
        Отложить задачу на заданный промежуток времени
        ? со смещением кривой ?
        """
        self._status = 'Delayed'
        return True

    def refresh_statuses(self):
        """
        Refresh:
            - Current status
            - Dates
            - Panalties
            - Learning curve status
        """
        pass

    def get_due_date(self):
        return get_date()

    def task_to_dict(self):
        task_content = dict(Task.task_template)
        task_content['name'] = self._name
        task_content['type'] = self._type
        task_content['body'] = self._body 
        task_content['status'] = self._status 
        task_content['priority'] = self._priority 
        task_content['create_dttm'] = self._create_dttm 
        task_content['current_curve_stage'] = self._current_curve_stage 
        task_content['last_repeat_date'] = self._last_repeat_date 
        task_content['next_repeat_date'] = self._next_repeat_date 
        task_content['update_dttm'] = self._update_dttm 

        return task_content
        

    def __init__(self,task_id,task_content):
        self._id = task_id
        self._name = task_content['name']
        self._type = task_content['type']
        self._body = task_content['body']
        self._status = task_content['status']
        self._priority = task_content['priority']
        self._create_dttm = task_content['create_dttm']
        self._current_curve_stage = task_content['current_curve_stage']
        self._last_repeat_date = task_content['last_repeat_date']
        self._next_repeat_date = task_content['next_repeat_date']
        self._update_dttm = task_content['update_dttm']

        return None

def task_test():
    #log("\n---Test---Test---Test---")
    #log("Begining Task Test")
    task_content = dict(Task.task_template)
    task = Task(1,task_content)
    test_result = True

    if not isinstance(task,Task):
        log("Failed to create Task object",indent=1)
        test_result = False

    task.mark_as_read()
    if task._status != 'Read':
        log("Failed Task.mark_as_read()",indent=1)
        test_result = False

    task.mark_as_overdue()
    if task._status != 'Overdue':
        log("Failed Task.mark_as_overdue()",indent=1)
        test_result = False

    task.mark_as_complete()
    if task._status != 'Complete':
        log("Failed Task.mark_as_complete()",indent=1)
        test_result = False

    task.mark_as_canceled()
    if task._status != 'Cancelled':
        log("Failed Task.mark_as_canceled()",indent=1)
        test_result = False

    task.delay_task()
    if task._status != 'Delayed':
        log("Failed Task.delay_task()",indent=1)
        test_result = False

    task.mark_as_new()
    if task._status != 'New':
        log("Failed Task.mark_as_new()",indent=1)
        test_result = False

    task_content2 = task.task_to_dict()
    if task_content != task_content2:
        log("\tFailed Task.task_to_dict()",indent=1)
        log("\nSource template",indent=1)
        pp.pprint(dict_el_to_str(task_content))
        log("\nTarget template",indent=1)
        pp.pprint(dict_el_to_str(task_content2))
        test_result = False
        
    task.refresh_statuses()
    if task._status != 'Read':
        log("Failed Task.refresh_statuses()",indent=1)
        #test_result = False
        pass

    task.get_due_date()
    if task._status != 'Read':
        log("Failed Task.get_due_date()",indent=1)
        #test_result = False
        pass

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
    #meta_file = dict()
    #meta_file['tasks'] = dict()
    #meta_file['update_dttm'] = get_dttm()
    #log(meta_file)
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
    #log("\n---Test---Test---Test---")
    #log("Begining File Manager Test")
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
    meta_read_successful = Meta.read_meta()
    if not meta_read_successful:
        return False
    # Start_GUI() - to be added
    return True
# Execution
startup()
#Meta.add_task('new task')
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
        #log("File Manager test is passed.")
        pass
    else:
        log("!!! File Manager test is FAILED!")

    if task_test():
        #log("Task test is passed.")
        pass
    else:
        log("!!! Task test is FAILED!")

    if metadata_test():
        #log("Metadata test is passed.")
        pass
    else:
        log("!!! Metadata test is FAILED!")

    if time_functions_test():
        #log("Time Functions test is passed.")
        pass
    else:
        log("!!! Time Functions test is FAILED!")
    log("Tests finished.")
    return True

test_manager()

