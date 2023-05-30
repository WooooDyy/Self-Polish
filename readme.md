## Self-Polish

Codes for the paper  [Self-Polsih: Enhance Reasoning in Large Language Models via Problem Refining.](https://arxiv.org/abs/2305.14497)

## Code Structure

- We use object-oriented style programming, and **decouple the codes on the question side and the answer side**. We can combine them for better performance. We implement the following methods not.

    - **Problem Side**: There are two strategies for problems:
      - **Self-Polish (The proposed method)**: The proposed method that optimizes problems till an converged answer is got.
      - **Normal**: The original method. No optimization is used upon problems.
      - <img src="https://spring-security.oss-cn-beijing.aliyuncs.com/img/image-20230530192959758.png" alt="image-20230530192959758" style="zoom:50%;" />
    - Answer Side: There are three strategies for answer generation:
      - **Few Shot**: Generate Answer with several examples.
      - **Few Shot CoT**: Generate Answer with several examples, and each example contains the chain-of-thought reasoining process.
      - **Least-to-Most**: Reduce problems to sub problems and then solve them one by one。
      - <img src="https://spring-security.oss-cn-beijing.aliyuncs.com/img/image-20230530192935854.png" style="zoom:50%;" />
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

### Method Figure
<img src="https://spring-security.oss-cn-beijing.aliyuncs.com/img/image-20230530212605407.png" alt="image-20230530212605407" style="zoom: 33%;" />

<img src="https://spring-security.oss-cn-beijing.aliyuncs.com/img/image-20230530212621727.png" alt="image-20230530212621727" style="zoom:33%;" />
