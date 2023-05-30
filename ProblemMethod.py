# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : Problem_Method.py
@Project  : SelfPolish
@Time     : 2023/5/30 14:06
@Author   : Zhiheng Xi
"""
from AnswerMethod import *

class ProblemMethod():
    def __init__(self,problem_method="Normal",answer_method: AnswerMethod =None):
        self.problem_method=problem_method
        assert answer_method is not None
        self.answer_method=answer_method
        pass
    def forward(self):
        pass
    def process_problem_for_one_time(self,question,answer,direct_answer_trigger_for_fewshot,dataset):
        cur_correctness=False
        try:
            cur_answer = self.answer_method.forward(question=question, answer=answer,
                                                 direct_answer_trigger_for_fewshot=direct_answer_trigger_for_fewshot,
                                                 dataset=dataset)
            # update
            if dataset == "aqua":
                if cur_answer == answer:
                    # original_correct += 1
                    cur_correctness = True
            else:
                if cur_answer == answer or float(cur_answer) == float(answer):
                    # original_correct += 1
                    cur_correctness = True
            return cur_answer,cur_correctness
        except Exception as e:
            raise e


class ProblemNormal(ProblemMethod):
    def __init__(self,problem_method="Normal",
                 answer_method: AnswerMethod =None, eng="text-davinci-003"):
        self.problem_method = problem_method
        assert answer_method is not None
        self.answer_method=answer_method
        self.eng=eng

    def forward(self,question,answer,direct_answer_trigger_for_fewshot,dataset,prompt_index):
        try:
            original_answer,original_correctness = self.process_problem_for_one_time(question=question,
                                          answer=answer,
                                          direct_answer_trigger_for_fewshot=direct_answer_trigger_for_fewshot,
                                          dataset=dataset,
                                          )
            return original_correctness, original_answer,None,None

        except Exception as e:
            if "RateLimitError" in repr(e) or "APIConnectionError" in repr(e) or "AuthenticationError" in repr(
                    e):
                # api exception
                raise e
            else:
                pass

        pass

class ProblemSelfPolish(ProblemMethod):
    def __init__(self,problem_method="SP", final_choose=None, max_times=None,answer_method=None,eng="text-davinci-003" ):
        self.problem_method=problem_method

        assert final_choose is not None
        assert max_times is not None
        assert answer_method is not None

        self.final_choose=final_choose
        self.max_times=max_times
        self.answer_method=answer_method
        self.eng=eng

        pass



    def generate_one_new_quesiton(self, eng, dataset, prompt_index, original_question):
        generate_rewrite_version_prompt_path = "prompt/my_prompts/rewrite_prompt/{}/{}_rewrite_prompt_{}.txt".format(
            dataset, dataset, prompt_index)
        with open(file=generate_rewrite_version_prompt_path, mode="r", encoding="utf-8") as f:
            generate_rewrite_version_prompt = f.read().strip()
        # if i == 0:
        #     print(f"\nmodel: {eng}")
        #     print(f"generate_rewrite_version_prompt_path: {generate_rewrite_version_prompt_path}\n")
        #     print(f"\ngenerate rewrite version prompt: {generate_rewrite_version_prompt}\n")
        prompt_input_to_generate_new_question = generate_rewrite_version_prompt + "\n\nOriginal: {}\nNew:".format(
            original_question)
        if eng in ["gpt-3.5-turbo", "gpt-4"]:

            new_generated_question = create_response_chat(
                eng=eng,
                prompt_input=[
                    {"role": "system",
                     "content": "Please rewrite new versions of the original mathematical question to be more understandable and easy to answer. Don't omit any useful information, especially the numbers, and please maintain their original meaning when polysemous words appear."},
                    {"role": "user", "content": prompt_input_to_generate_new_question}
                ],
                temperature=0,
                max_tokens=256
            )
            new_generated_question = new_generated_question["choices"][0]["message"]["content"]
            time.sleep(21)
        else:
            new_generated_question = create_response(
                eng=eng,
                prompt_input=prompt_input_to_generate_new_question,
                temperature=0,
                max_tokens=256
            )["choices"][0]["text"]
        return new_generated_question

    def forward(self,question,answer,direct_answer_trigger_for_fewshot,dataset,prompt_index):

        original_answer = None
        original_correctness=False
        consistent_correctness=False


        consistent_answer = None
        vote_answer = None
        convergence_flag = True
        times = 0


        try:
            print("Processing Original Question.")
            original_answer,original_correctness = self.process_problem_for_one_time(question=question,
                                          answer=answer,
                                          direct_answer_trigger_for_fewshot=direct_answer_trigger_for_fewshot,
                                          dataset=dataset,
                                          )

        except Exception as e:
            if "RateLimitError" in repr(e) or "APIConnectionError" in repr(e) or "AuthenticationError" in repr(
                    e):
                raise e
            else:
                pass


        last_answer = original_answer
        last_question = question
        print("------------------------------------------------------------")
        print("Self-Polish start!")
        all_answers = [original_answer]
        try:
            while True:
                time.sleep(1.5)
                times += 1
                if times >= self.max_times:
                    convergence_flag = False
                    vote_answer = max(all_answers, key=all_answers.count)
                    cnt = all_answers.count(max(all_answers, key=all_answers.count))
                    if cnt == 1:
                        vote_answer = original_answer
                    else:
                        vote_answer = vote_answer

                    if self.final_choose == "original":
                        consistent_answer = original_answer
                    elif self.final_choose == "last_one":
                        consistent_answer = last_answer
                    elif self.final_choose == "first_one":
                        consistent_answer = first_answer
                    elif self.final_choose == "vote":
                        consistent_answer = vote_answer

                    print("More than {} times!".format(self.max_times))
                    break
                try:
                    # new problem
                    new_generated_question = self.generate_one_new_quesiton(
                        eng=self.eng,
                        dataset=dataset,
                        prompt_index=prompt_index,
                        original_question=last_question
                    )
                    print("The {} times generated: {}".format(times, new_generated_question))

                    # new answer
                    new_answer,new_correctness = self.process_problem_for_one_time(question=new_generated_question,
                                              answer=answer,
                                              direct_answer_trigger_for_fewshot=direct_answer_trigger_for_fewshot,
                                              dataset=dataset,
                                              )
                    if times == 1:
                        first_answer = new_answer

                    if dataset == "aqua" or dataset=="mathqa":
                        if last_answer != None and new_answer != None and last_answer == new_answer:
                            print("Answer Converged!")
                            consistent_answer = new_answer
                            break
                    else:
                        if last_answer != None and new_answer != None and (
                                last_answer == new_answer or float(last_answer) == float(new_answer)):
                            print("Answer Converged!")
                            consistent_answer = new_answer
                            break
                except Exception as e:
                    print(repr(e))
                    traceback.print_exc()
                    if "RateLimitError" in repr(e) or "APIConnectionError" in repr(e):
                        raise e
                        break
                    else:
                        continue
                last_answer = new_answer
                last_question = new_generated_question
                all_answers.append(new_answer)

            print("------------------------------------------------------------")

            if dataset == "aqua" or dataset == "mathqa":
                if consistent_answer == answer:
                    consistent_correctness = True
            else:
                if consistent_answer == answer or float(consistent_answer) == float(answer):
                    consistent_correctness = True

            if consistent_correctness and not original_correctness:
                print("Consistent Question is better!")
                print("Original Question: {}".format(question))
                print("Final Question: {}".format(new_generated_question))
                winner = "new"
            elif not consistent_correctness and original_correctness:
                print("Original Question is better!")
                print("Original Question: {}".format(question))
                print("Final Question: {}".format(new_generated_question))
                winner = "origin"
            elif consistent_correctness and original_correctness:
                print("Original Question and Consistent Question are both good!")
                winner = "tie"

            else:
                print("Original Question and Consistent Question are both bad!")
                winner = "tie"

        except Exception as e:
            print(repr(e))
            traceback.print_exc()
            if "RateLimitError" in repr(e) or "APIConnectionError" in repr(e) or "AuthenticationError" in repr(e):
                raise e
            else:
                return original_correctness,original_answer,consistent_correctness,consistent_answer

        return original_correctness, original_answer, consistent_correctness, consistent_answer


if __name__ == '__main__':
    pass
