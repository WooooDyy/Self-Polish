nohup python -u test_problem_method_with_exception.py --dataset gsm8k\
 --method few_shot --method2 SP\
  --final_choose "last_one" \
  --max_times 3 --file_type "test"\
   --eng text-davinci-003 --num_test 20 --prompt_index 0 &