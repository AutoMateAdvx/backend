import os
import tempfile
from dotenv import load_dotenv
from flow import create_flow, create_adaptive_flow
from agentflow.utils.crawl_github_files import clone_repository, get_or_clone_repository, filter_and_read_files, get_commit_changes, get_commit_changes_detailed, get_exclude_patterns, get_file_patterns, checkout_to_commit
# Load environment variables from .env file
load_dotenv()

def test_original_flow():
    """测试原始的关卡生成流程"""
    print("=== 测试原始流程 ===")
    repo_url = "https://github.com/zengyi-thinking/auto_mate_test3_call"
    shared = {
        "currentIndex": 5,
        "language": "中文",
        "use_cache": True,
        "max_abstraction_num": 5,
        "project_name": repo_url, 
    }
    
    flow = create_flow()
    flow.run(shared)
    print("原始流程结果:")
    print(shared.get("res", "无结果"))

def test_adaptive_flow():
    """测试自适应的关卡生成流程"""
    print("\n=== 测试自适应流程 ===")
    repo_url = "https://github.com/zengyi-thinking/auto_mate_test3_call"
    
    try:
        # 克隆或获取仓库
        print("正在克隆/获取仓库...")
        repo = get_or_clone_repository(repo_url, update_to_latest=False)
        tmpdirname = repo.working_dir
        
        # 设置共享数据
        shared = {
            "tmpdirname": tmpdirname,
            "project_name": repo_url,
            "currentIndex": 2,  # 从较早的提交开始测试
            "repo": repo,
            "language": "中文",
            "use_cache": True,
            "max_abstraction_num": 5,
        }
        
        print(f"开始从提交索引 {shared['currentIndex']} 进行自适应分析...")
        
        # 创建并运行自适应流程
        flow = create_adaptive_flow()
        result = flow.run(shared)
        
        # 输出结果
        print("\n=== 自适应流程执行结果 ===")
        
        # 检查上下文评估结果
        context_eval = shared.get("context_evaluation", {})
        if context_eval:
            print(f"✅ 上下文评估完成:")
            print(f"   - 是否值得作为关卡: {context_eval.get('is_worthy', False)}")
            print(f"   - 最终提交索引: {context_eval.get('final_commit_index', 'N/A')}")
            print(f"   - 处理的提交数: {context_eval.get('commits_processed', 'N/A')}")
            print(f"   - 评估原因: {context_eval.get('evaluation', {}).get('reason', 'N/A')}")
            
            if context_eval.get('is_worthy'):
                print(f"   - 关键概念: {context_eval.get('evaluation', {}).get('key_concepts', [])}")
        
        # 检查知识点识别结果
        knowledge = shared.get("knowledge", [])
        if knowledge:
            print(f"\n📚 识别的知识点 ({len(knowledge)}个):")
            for i, concept in enumerate(knowledge, 1):
                print(f"   {i}. {concept.get('name', 'N/A')}")
                print(f"      描述: {concept.get('description', 'N/A')[:100]}...")
        
        # 检查生成的关卡内容
        level_content = shared.get("res")
        if level_content:
            print(f"\n🎯 生成的关卡内容:")
            if isinstance(level_content, list):
                for i, level in enumerate(level_content, 1):
                    print(f"   关卡 {i}: {level.get('name', 'N/A')}")
                    print(f"   描述: {level.get('description', 'N/A')[:150]}...")
                    print(f"   要求: {level.get('requirements', 'N/A')[:100]}...")
                    print()
            else:
                print(f"   {level_content}")
        else:
            print("❌ 未生成关卡内容")
            
        # 检查最终的提交索引
        final_index = shared.get("currentIndex")
        print(f"\n📍 最终提交索引: {final_index}")
        
    except Exception as e:
        print(f"❌ 自适应流程执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数：运行两种流程的测试"""
    print("开始测试关卡生成流程...")
    
    # 可以选择运行哪个测试
    run_original = False
    run_adaptive = True

    if run_adaptive:
        try:
            test_adaptive_flow()
        except Exception as e:
            print(f"自适应流程测试失败: {str(e)}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
