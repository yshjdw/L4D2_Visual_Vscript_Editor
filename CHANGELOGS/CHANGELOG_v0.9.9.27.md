# v0.9.9.27

- EntFire 默认 target=worldspawn, action=RunScriptCode。
- DoEntFire 同样默认 target=worldspawn、action=RunScriptCode。
- 修复 EntFire 文档中的参数解析异常（value/delay/activator）。
- 自定义 Function 标题旁增加“字符串调用”拖动入口，生成可嵌套表达式，用于 EntFire 的 value 槽。
- 函数参数可直接填写 env.userid 等表达式，生成的调用字符串不立即执行函数。
