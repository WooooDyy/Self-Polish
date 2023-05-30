## Self-Polish

Codes for the paper  [Self-Polsih: Enhance Reasoning in Large Language Models via Problem Refining.](https://arxiv.org/abs/2305.14497)



## Code Structure

- We use object-oriented style programming. There are two types of strategies for reasoning, and we can combine them for better performance.

    - Problem Side: There are two strategies for problems:
      - Self-Polish: The proposed method that optimizes problems till an converged answer is got.
      - Normal: The original method. No optimization is used upon problems.
      - ![image-20230530192959758](https://spring-security.oss-cn-beijing.aliyuncs.com/img/image-20230530192959758.png)
    - Answer Side: There are three strategies for answer generation:
      - Few Shot: Generate Answer with several examples.
      - Few Shot CoT: Generate Answer with several examples, and each example contains the chain-of-thought reasoining process.
      - Least-to-Most: Reduce problems to sub problems and then solve them one by one。
      - ![](https://spring-security.oss-cn-beijing.aliyuncs.com/img/image-20230530192935854.png)
- We also list some test prompts to rewrite problems in the prompt directory.
### Run Code

```bash
sh test_normal.sh
sh test_sp.sh
```

- Note that you should set your OpenAI API key in the `test_Normal_with_exception.py` or `test_SP_with_exception.py`:
```python
keys = ["Your Key"]
```
