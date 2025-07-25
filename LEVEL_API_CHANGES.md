# 关卡API修改说明

## 🎯 修改目标

将关卡API的 `/levels/get` 端点修改为：
- 接收课程ID和关卡ID作为参数
- 获取对应Git提交的文件内容
- 返回树形结构的文件数据

## 📋 修改内容

### 1. Schema修改 (`app/schemas/level.py`)

#### 新增文件树节点结构
```python
class FileTreeNode(BaseModel):
    """文件树节点"""
    type: str = Field(..., description="节点类型: file 或 directory")
    uri: str = Field(..., description="文件URI")
    children: Optional[List['FileTreeNode']] = Field(None, description="子节点（仅目录有）")
    content: Optional[str] = Field(None, description="文件内容（仅文件有）")
```

#### 修改请求模式
```python
class LevelGetRequest(BaseModel):
    """获取关卡详情的请求模式"""
    course_id: int = Field(..., description="课程ID")
    level_id: int = Field(..., description="关卡ID")
```

#### 修改响应模式
```python
class LevelResponse(BaseModel):
    # ... 原有字段 ...
    file_tree: Optional[FileTreeNode] = Field(None, description="项目文件树结构")
```

### 2. 文件树构建工具 (`app/utils/file_tree_builder.py`)

新增工具函数：
- `build_file_tree_from_files()` - 从文件字典构建树结构
- `sort_file_tree()` - 对文件树排序
- `filter_file_tree_by_patterns()` - 按模式过滤文件树
- `get_file_tree_stats()` - 获取文件树统计信息

### 3. API路由修改 (`app/routers/levels.py`)

#### 核心逻辑流程
1. **验证参数** - 检查课程ID和关卡ID的有效性
2. **获取课程信息** - 从数据库获取Git仓库URL
3. **克隆仓库** - 临时克隆Git仓库
4. **重置到指定提交** - 根据关卡顺序号计算提交索引
5. **获取文件** - 使用文件模式过滤获取代码文件
6. **构建文件树** - 将文件转换为树形结构
7. **返回响应** - 包含关卡信息和文件树

#### 关键代码片段
```python
# 计算提交索引（关卡顺序号 + 1，因为从第2个提交开始）
current_index = level_result.order_number + 1

# 重置到指定提交
commits = list(repo.iter_commits(reverse=True))
reset_to_commit(repo, commits, current_index)

# 获取文件
result = filter_and_read_files(
    tmpdirname,
    max_file_size=1 * 1024 * 1024,
    include_patterns=get_file_patterns("code"),
    exclude_patterns=get_exclude_patterns("common")
)

# 构建文件树
project_name = course.git_url.split('/')[-1].replace('.git', '')
base_uri = f"file:///github/{project_name}"
file_tree = build_file_tree_from_files(result["files"], base_uri)
```

## 🔧 API使用方式

### 请求格式
```http
POST /levels/get
Content-Type: application/json

{
    "course_id": 1,
    "level_id": 3
}
```

### 响应格式
```json
{
    "id": 3,
    "course_id": 1,
    "title": "函数定义与调用",
    "description": "学习如何在Python中定义和调用函数",
    "requirements": "创建一个简单的函数并调用它",
    "order_number": 3,
    "file_tree": {
        "type": "directory",
        "uri": "file:///github/auto_mate_test2",
        "children": [
            {
                "type": "file",
                "uri": "file:///github/auto_mate_test2/hello_world.py",
                "content": "print('Hello, World!')"
            }
        ]
    }
}
```

## 🧪 测试验证

### 测试文件
- `test_level_api.py` - 核心功能测试
- `level_api_example.py` - API使用示例

### 测试结果
✅ 成功克隆Git仓库  
✅ 正确重置到指定提交  
✅ 获取并过滤代码文件  
✅ 构建树形文件结构  
✅ 返回正确的JSON格式  

### 测试输出示例
```
重置到第 3 个提交: a8a51103 - hello_world基础入门
获取到 1 个文件
✅ 成功生成文件树，根节点类型: directory
   根URI: file:///github/auto_mate_test2
   子节点数量: 1
```

## 📊 功能特性

### ✅ 已实现功能
- [x] 接收课程ID和关卡ID参数
- [x] 验证关卡属于指定课程
- [x] 根据关卡顺序号计算Git提交索引
- [x] 克隆Git仓库并重置到指定提交
- [x] 过滤获取代码文件（排除.git、node_modules等）
- [x] 构建树形文件结构
- [x] 包含文件内容在响应中
- [x] 错误处理和资源清理
- [x] 完整的测试验证

### 🔄 提交索引映射
- 关卡1 → Git提交2（第2个提交）
- 关卡2 → Git提交3（第3个提交）
- 关卡N → Git提交N+1

### 📁 文件过滤规则
**包含模式（代码文件）：**
- `*.py`, `*.js`, `*.ts`, `*.java`, `*.cpp`, `*.c`, `*.h`
- `*.cs`, `*.go`, `*.rs`, `*.php`

**排除模式（常见无用文件）：**
- `*/node_modules/*`, `*/.git/*`, `*/venv/*`
- `*/__pycache__/*`, `*.pyc`, `*/dist/*`, `*/build/*`

## 🚀 部署说明

### 依赖要求
- FastAPI
- SQLAlchemy
- GitPython
- Pydantic v2

### 环境配置
确保服务器有Git访问权限，能够克隆指定的Git仓库。

### 性能考虑
- 使用临时目录避免磁盘占用
- 自动清理临时文件
- 文件大小限制（默认1MB）
- 只获取代码文件，排除二进制文件

## 🎉 总结

成功实现了关卡API的增强功能：
1. **参数升级** - 从单一关卡ID到课程ID+关卡ID
2. **Git集成** - 动态获取对应提交的文件内容
3. **树形结构** - 以标准文件树格式返回项目结构
4. **内容包含** - 直接在响应中包含文件内容
5. **完整测试** - 提供测试工具和使用示例

这个API现在可以为前端提供完整的项目文件结构，支持代码编辑器、文件浏览器等功能的实现。