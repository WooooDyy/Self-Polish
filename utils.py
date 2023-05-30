import json
import re
from statistics import mean

def get_dataset_path(dataset,file_type,ori_path):
    dataset_path = {"gsm8k": "gsm8k/{}.jsonl".format(file_type)}
    res_path = "{}/{}".format(ori_path,dataset_path[dataset])
    return res_path


def read_jsonl(path: str):
    with open(path, "r", encoding='utf-8') as fh:
        return [json.loads(line) for line in fh.readlines() if line]


def extract_nums(s):
    s = s.replace(",", "")
    # s = s.replace(".", "")
    s = s.replace("$", "")

    nums = re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", s)
    return_list = []
    for i in range(len(nums)):
        try:
            return_list.append(eval(nums[i].strip().lstrip(" 0")))
        except:
            pass
    return return_list


def find_formula(step):
    assert step.count("<<") == step.count(">>") == 1
    left, right = step.find("<<")+2, step.find(">>")
    return step[left: right]


def extract_answer(completion):
    ANS_RE = re.compile(r"#### (-?[0-9.,]+)")
    match = ANS_RE.search(completion)
    if match:
        match_str = match.group(1).strip()
        match_str = match_str.replace(",", "")
        return match_str
    else:
        assert False


def delete_extra_zero(n):
    try:
        n = float(n)
    except:
        print("None {}".format(n))
        return n
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        n = str(n).rstrip('0')  # 删除小数点后多余的0
        n = int(n.rstrip('.')) if n.endswith('.') else float(n)  # 只剩小数点直接转int，否则转回float
        n = str(n)
        return n


def make_print_to_file(file_name='./', path="./", output_csv_path=None):
    '''
    path， it is a path for save your log about fuction print
    example:
    use  make_print_to_file()   and the   all the information of funtion print , will be write in to a log file
    :return:
    '''
    import os
    import sys
    import time
    import datetime
    import pytz

    class Logger(object):
        def __init__(self, filename, path="./"):
            self.terminal = sys.stdout
            # todo add or write?
            self.log = open(filename, "a", encoding='utf8')
            # self.log = open(filename, "w", encoding='utf8')
            if not os.path.exists(filename):
                with open(output_csv_path, 'a+', encoding='utf-8') as f:
                    f.write("")

        def write(self, message):
            # self.terminal.write(message)
            if message != "\n" and message != "\r":
                message = str(datetime.datetime.now(pytz.timezone('Asia/Shanghai'))) + "   " + message

            self.terminal.write(message)
            self.log.write(message)
            self.log.flush()

        def flush(self):
            pass

    # fileName = time.strftime(file_name+'%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    sys.stdout = Logger(file_name, path=path)

def data_reader(dataset,dataset_path):
    questions = []
    answers = []
    decoder = json.JSONDecoder()

    if dataset == "gsm8k":
        with open(dataset_path) as f:
            lines = f.readlines()
            for line in lines:
                json_res = decoder.raw_decode(line)[0]
                questions.append(json_res["question"].strip())
                answers.append(delete_extra_zero(json_res["answer"].split("#### ")[-1].replace(",", "")))

    elif dataset == "gsmic":
        with open(dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["new_question"]
                a = str(line["answer"]).replace(",","")
                questions.append(q)
                answers.append(delete_extra_zero(a))

    elif dataset == "aqua":
        with open(dataset_path) as f:
            lines = f.readlines()
            for line in lines:
                json_res = decoder.raw_decode(line)[0]
                choice = "(" + "(".join(json_res["options"])
                choice = choice.replace("(", " (").replace(")", ") ")
                choice = "Answer Choices:" + choice
                questions.append(json_res["question"].strip() + " " + choice)
                answers.append(json_res["correct"])

    elif dataset in ("addsub", "singleeq"):
        with open(dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["sQuestion"].strip()
                a = str(line["lSolutions"][0])
                if a[-2:] == ".0":
                    a = a[:-2]
                questions.append(q)
                answers.append(delete_extra_zero(a))

    elif dataset in ("svamp", "multiarith"):
        with open(dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["question"].strip()
                a = str(line["answer"])
                if a[-2:] == ".0":
                    a = a[:-2]
                questions.append(q)
                answers.append(delete_extra_zero(a))
    else:
        raise ValueError("dataset is not properly defined ...")

    q_len_list = []
    for q in questions:
        q_len_list.append(len(q.split(" ")))
    q_len_mean = mean(q_len_list)
    print("dataset : {}".format(dataset))
    print("data size : {}".format(len(answers)))
    print("average num of words for each sample : {}".format(q_len_mean))
    return questions, answers

def answer_cleansing(method,direct_answer_trigger_for_fewshot,dataset, pred):
    # print("pred_before : " + pred)

    if method in ("few_shot", "few_shot_cot","least_to_most"):
        preds = pred.split(direct_answer_trigger_for_fewshot)
        answer_flag = True if len(preds) > 1 else False
        pred = preds[-1]

    if dataset == "aqua":
        pred = pred.upper()
        pred = re.findall(r'A|B|C|D|E', pred)


    elif dataset in ("gsm8k", "addsub", "multiarith", "svamp", "singleeq","gsmic"):
        pred=pred.replace(",", "")
        pred = [delete_extra_zero(s.replace(",", "")) for s in re.findall(r'-?\d+/?\.?\d*', pred)]
    else:
        raise ValueError("dataset is not properly defined ...")

    # If there is no candidate in list, null is set.
    if len(pred) == 0:
        pred = ""
    else:
        if method in ("few_shot", "few_shot_cot","least_to_most"):
            if answer_flag:
                # choose the first element in list ...
                pred = pred[0]
            else:
                # choose the last element in list ...
                pred = pred[-1]
        elif method in ("zero_shot", "zero_shot_cot"):
            # choose the first element in list ...
            pred = pred[0]
        else:
            raise ValueError("method is not properly defined ...")

    # (For arithmetic tasks) if a word ends with period, it will be omitted ...
    if pred != "":
        if pred[-1] == ".":
            pred = pred[:-1]
        if pred[-1] == "/":
            pred = pred[:-1]


    return pred

