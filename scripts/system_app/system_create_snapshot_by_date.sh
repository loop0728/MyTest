#!/bin/bash

#############################################################################################################
# 名称: system_create_snapshot_by_date.sh
# 版本: 1.0
# 日期: 2024-05-07
# 描述:
#		这个脚本实现了在alkaid目录根据模板snapshot.xml获取指定日期各仓库当天最后一笔提交
#		并组成新的snapshot.xml以方便用户通过repo抓取指定日期的alkaid代码包
# 注意:
#		如果指定日期当天找不到任何提交，则会向前向后进行遍历设定的天数，若最终找不到则使用模板默认revision值
#		NUMBER_OF_DAYS_TO_TRAVERSE_FORWARD=7
#		NUMBER_OF_DAYS_TO_TRAVERSE_BACKWARD=7
#############################################################################################################

# 定义往前往后遍历的天数
NUMBER_OF_DAYS_TO_TRAVERSE_FORWARD=30
NUMBER_OF_DAYS_TO_TRAVERSE_BACKWARD=7
# 模板路径确认次数
NUMBER_OF_TEMPLATE_CONFIRMATIONS=5

# 打印使用说明
function sstar_create_snapshot_print_usage() {
	echo -e "========================================================================================================"
	echo -e "\e[31m注意:\e[0m"
	echo -e "\e[31m	1. $0 路径必须在alkaid根目录\e[0m"
	echo -e "\e[31m	2. 请先在alkaid目录生成基础的snapshot.xml模板，可使用：repo manifest -r -o snapshot.xml\n\e[0m"
    echo -e "\e[33m用法:\e[0m"
	echo -e "\e[33m	$0 <日期> <snapshot.xml路径>\n\e[0m"
	echo -e "\e[32m示例:\e[0m"
    echo -e "\e[32m	$0 20240430 snapshot.xml\e[0m"
	echo -e "\e[32m	$0 20240430 ./snapshot.xml\e[0m"
    echo -e "\e[32m	$0 20240430 ../../snapshot.xml\e[0m"
	echo -e "\e[32m	$0 20240430 /home/jason.yang/workspace/i6dw/alkaid/snapshot.xml\e[0m"
	echo -e "========================================================================================================"
}

function sstar_create_snapshot_countdown() {
    secs=$1
    while [ $secs -gt 0 ]; do
        echo -ne "剩余时间: $secs 秒\033[0K\r"
        sleep 1
        : $((secs--))
    done
    echo "倒计时结束！"
}

# 函数：将日期格式化为 YYYY-MM-DD
function sstar_create_snapshot_format_date() {
    date -d "$1" +%Y-%m-%d
}

# 函数：将日期格式化为 YYYYMMDD
function sstar_create_snapshot_reformat_date() {
    date -d "$1" +%Y%m%d
}

function sstar_create_snapshot_do_repo_sync() {
    repo forall -c 'git pull origin $REPO_RREV' && repo forall -c 'git clean -df' && repo sync -c -j32
}

function sstar_create_snapshot_do_generate() {
    repo manifest -r -o $1
}

function sstar_create_snapshot_create_snapshot_templates()
{
	# 提示用户是否需要手动对alkaid进行repo sync并生成snapshot.xml
	while true; do
		read -p "是否需要进行 repo sync 操作？(Y/N): " choice

		case "$choice" in
		  y|Y )
			echo "执行repo sync操作..."
			# 在这里执行repo sync操作的命令
			sstar_create_snapshot_do_repo_sync
			echo -e "\e[32mrepo sync操作已完成！\e[0m"
			break
			;;
		  n|N )
			echo -e "\e[31m取消repo sync操作.\e[0m"
			break
			;;
		  * )
			echo -e "\e[31m无效的选项，请输入Y或N.\e[0m"
			continue
			;;
		esac
	done
	create_snapshot_flag=0
	# 提示用户是否需要手动对alkaid进行repo sync并生成snapshot.xml
	while true; do
		read -p "是否需要生成模板snapshot.xml文件操作？(Y/N): " choice

		case "$choice" in
		  y|Y )
			echo "生成模板 $1 文件..."
			if [ -e "$1" ]; then
				echo -e "\e[31m$1 文件已存在\e[0m"
				while true; do
					read -p "是否需要进行覆盖生成模板$default_snapshot_file文件？(Y/N): " choice

					case "$choice" in
					  y|Y )
						echo "即将进行覆盖生成模板 $1 文件的操作 ..."
						echo "输入参数:$1"
						sstar_create_snapshot_do_generate $1
						create_snapshot_flag=1
						echo -e "\e[32m覆盖生成模板 $1 文件已完成！\e[0m"
						break
						;;
					  n|N )
						echo -e "\e[31m取消覆盖生成模板$default_snapshot_file文件操作.\e[0m"
						break
						;;
					  * )
						echo -e "\e[31m无效的选项，请输入Y或N.\e[0m"
						continue
						;;
					esac
				done
			else
				echo -e "\e[31m输入参数:$1 文件不存在，生成中 ...\e[0m"
				sstar_create_snapshot_do_generate $1
				create_snapshot_flag=1
				if [ -e "$1" ]; then
					echo -e "\e[33m$1已生成\e[0m"
				else
					echo -e "\e[31m$1 生成失败！\e[0m"
				fi
			fi
			break
			;;
		  n|N )
			echo -e "\e[31m取消生成模板 $1 文件的操作.\e[0m"
			break
			;;
		  * )
			echo -e "\e[31m无效的选项，请输入Y或N.\e[0m"
			continue
			;;
		esac
	done
}

function sstar_create_snapshot_input_param_chk() {
	# 获取日期参数
	date_input="$1"

	# 如果只提供了一个参数且是文件路径，则使用当前日期作为默认值
	if [ $# -eq 1 ] && [ -f "$1" ]; then
		echo "未提供日期参数，默认使用当前日期。"
		date_input=$(date +"%Y%m%d")
	fi

	# 格式化日期
	date=$(sstar_create_snapshot_format_date "$date_input")

	# 获取snapshot.xml路径参数
	snapshot_file="$2"

	# 如果参数数量不为2，或者参数为2但日期或文件路径格式不正确，则打印使用说明并退出
	if [ $# -ne 2 ] || ! [[ $date_input =~ ^[0-9]{8}$ ]] || [ ! -f "$snapshot_file" ]; then
		sstar_create_snapshot_print_usage
		# 提示用户选择
		while true; do
			read -p "Do you want to set it manual? (Yy(es)/Nn(o)): " choice

			# 将用户输入转换为小写
			choice=$(echo "$choice" | tr '[:upper:]' '[:lower:]')

			# 判断用户的选择
			if [[ "$choice" == "yes" || "$choice" == "y" ]]; then
				echo "You chose to continue."
				# 在这里执行你想要执行的逻辑
				# 设置默认日期
				default_date=$(date +"%Y%m%d")

				# 提示输入日期
				read -p "请输入日期（格式：YYYYMMDD，默认为当前日期） [$default_date]: " date_input

				# 如果输入为空，则使用默认日期
				date="${date_input:-$default_date}"

				# 校验日期格式
				while ! [[ $date =~ ^[0-9]{4}[0-9]{2}[0-9]{2}$ ]]; do
					read -p "日期格式不正确，请重新输入（格式：YYYY-MM-DD，默认为当前日期） [$default_date]: " date_input
					date="${date_input:-$default_date}"
				done

				# 获取脚本所在目录
				script_dir=$(dirname "$(realpath "$0")")

				# 设置默认文件路径为脚本所在目录下的snapshot.xml
				default_snapshot_file="$script_dir/snapshot.xml"

				# 提示用户是否需要手动对alkaid进行repo sync并生成snapshot.xml
				sstar_create_snapshot_create_snapshot_templates $default_snapshot_file

				# 提示输入文件路径
				read -p "请输入snapshot.xml文件路径（默认为当前目录下的snapshot.xml） [$default_snapshot_file]: " snapshot_file

				# 如果输入为空，则使用默认文件路径
				snapshot_file="${snapshot_file:-$default_snapshot_file}"

				# 校验文件路径
				loop_cnt=0 # 方便用户反悔想重新repo sync & 生成snapshot
				quit_enter_snapshot_loop_flag=0
				while [ ! -f "$snapshot_file" ]; do
					((loop_cnt++))
					if [ "$loop_cnt" -eq $NUMBER_OF_TEMPLATE_CONFIRMATIONS ]; then
						read -p "已经输入 $NUMBER_OF_TEMPLATE_CONFIRMATIONS 次snapshot模板文件路径错误，是否继续输入？(Y/y：继续输入，N/n：退出当前输入界面并重新选择是否需要手动对alkaid进行repo sync并生成snapshot.xml): " choice

						case "$choice" in
							y|Y )
								loop_cnt=0
								continue
								;;
							n|N )
								echo -e "\e[31m退出手动输入snapshot模板文件路径循环\e[0m"
								# 提示用户是否需要手动对alkaid进行repo sync并生成snapshot.xml
								sstar_create_snapshot_create_snapshot_templates $default_snapshot_file
								quit_enter_snapshot_loop_flag=1
								break
								;;
							* )
								echo -e "\e[31m无效的选项，请输入Y/y或N/n.\e[0m"
								;;
						esac
					fi
					read -p "文件 $snapshot_file 不存在，请重新输入文件路径（默认为当前目录下的snapshot.xml） [$default_snapshot_file]: " snapshot_file
					snapshot_file="${snapshot_file:-$default_snapshot_file}"
				done
				break  # 选择有效，跳出循环
			elif [[ "$choice" == "no" || "$choice" == "n" ]]; then
				echo -e "\033[41;30mYou chose not to continue. Please refer to usage to re-execute the script!\033[0m"
				# 在这里执行你想要执行的另一套逻辑
				exit 1
			else
				echo -e "\e[31mInvalid choice. Please choose either 'yes' or 'no'.\e[0m"
			fi
		done

		# 如果用户选择退出手动输入snapshot模板文件路径 并且 没有执行repo sync与生成snapshot的动作，则要报错退出，并提示必须要有模板snapshot文件才可以
		if [ "$quit_enter_snapshot_loop_flag" -eq 1 ]; then
			if [ "$create_snapshot_flag" -eq 0 ]; then
				echo "必须要存在模板snapshot.xml文件才可以，递归调用sstar_create_snapshot_input_param_chk $1 $2"
				# 递归调用参数检查
				sstar_create_snapshot_input_param_chk $1 $2
			else
				# 使用默认文件路径
				snapshot_file="$default_snapshot_file"
				echo "使用模板默认文件路径：$snapshot_file"
			fi
		fi

		# 打印结果
		# 格式化日期
		date=$(sstar_create_snapshot_format_date "$date")
		echo "日期: $date"
		echo "设置（多次交互）的snapshot.xml路径: $snapshot_file"
	else
		# 如果日期参数为默认值，提示用户
		if [ "$date_input" == "$(date +"%Y%m%d")" ]; then
			echo "使用的是当前日期，如有必要，请检查日期参数。"
		fi

		# 转换snapshot.xml路径为绝对路径
		snapshot_file=$(realpath "$snapshot_file")

		# 打印结果
		echo "日期: $date"
		echo "设置（带参数且参数正确）的snapshot.xml路径: $snapshot_file"
	fi
}

function sstar_create_snapshot_check_alkaid_path() {
	# 初始目录
	current_dir=$(pwd)
	process_path=""
	echo -e "\e[33m当前脚本文件$0所在的路径为：$current_dir\e[0m"

	# 遍历往上查找目录
	while [ "$current_dir" != "/" ]; do
		if [ "$(basename "$current_dir")" == "alkaid" ]; then
			process_path="$current_dir"
			break
		fi
		current_dir=$(dirname "$current_dir")
	done

	# 判断是否找到目录
	if [ -z "$process_path" ]; then
		echo -e "\e[33m未找到目录 alkaid, 请注意当前脚本文件 $0 只能放置在alkaid及其子目录任意位置\e[0m"
		exit 1
	else
		echo -e "\e[33m向上找到目录 alkaid: $process_path 并进入该目录执行相关操作！\e[0m"
		cd "$process_path" || exit
	fi

	echo "已切换工作路径为：$current_dir"

	# 先判断文件路径是否正确
	# 获取当前目录名称
	current_dir=$(basename "$PWD")

	# 检查上一级目录名称是否为aaa
	if [ "$current_dir" != "alkaid" ]; then
		echo "当前目录名称不是alkaid"
		exit 1
	fi

	# 检查当前路径下是否有"boot" "kernel" "project" "sdk" "build" "rtos" "pm_rtos" "optee"目录
	required_dirs=("boot" "kernel" "project" "sdk" "build" "rtos" "pm_rtos" "optee")
	missing_dirs=()

	for dir in "${required_dirs[@]}"; do
		if [ ! -d "$dir" ]; then
			missing_dirs+=("$dir")
		fi
	done

	if [ ${#missing_dirs[@]} -eq 0 ]; then
		echo "当前工作目录名称为alkaid，并且该路径下有以下目录：${required_dirs[*]}"
	else
		echo "当前工作目录名称为alkaid，但该路径下缺少以下目录：${missing_dirs[*]}"
		exit 1
	fi
}

function sstar_create_snapshot_ergodic_process() {
	# 如果未找到提交记录，则往前遍历 $NUMBER_OF_DAYS_TO_TRAVERSE_FORWARD 天
	for ((i = 1; i <= $NUMBER_OF_DAYS_TO_TRAVERSE_FORWARD; i++)); do
		prev_date=$(date -d "$date - $i day" +%Y-%m-%d)
		echo "尝试往前查找 $prev_date 的提交记录"
		echo "尝试往前查找 $prev_date 的提交记录" >> "$log_file"
		commits=()
		commiters=()
		# 获取提交commit id
		commits=($(git log --since="$(date -d "$prev_date - 1 day" +%Y-%m-%d)" --until="$prev_date" --pretty=format:"%H"))
		# 获取对应author
		commiters=($(git log --since="$(date -d "$prev_date - 1 day" +%Y-%m-%d)" --until="$prev_date" --pretty=format:"%an"))
		# 根据commit id进行处理
		if [ ${#commits[@]} -gt 0 ]; then
			last_commit="${commits[0]}"
			# 替换版本号
			echo -e "\e[33m已找到 $project_path($git_repository_name) 在 $prev_date 的提交记录如下：\e[0m"
			echo "已找到 $project_path($git_repository_name) 在 $prev_date 的提交记录如下：" >> "$log_file"
			#echo -e "\e[33m	${commits[@]}\e[0"
			echo -e "\e[33m	打印根据提交时间先后由下到上排序，最上面为最后一笔\e[0m"
			echo "	打印根据提交时间先后由下到上排序，最上面为最后一笔" >> "$log_file"
			echo -e "\e[33m	序号	commit ID					commiter	\e[0m"
			echo "	序号	commit ID				commiter	" >> "$log_file"
			#for commit in "${commits[@]}"; do
			#	echo -e "\e[33m	$commit\e[0m"
			#	echo "	$commit" >> "$log_file"
			#done
			for ((j=0; j<${#commits[@]}; j++)); do
				echo -e "\e[33m	$j.	${commits[j]}	${commiters[j]}	\e[0m"
				echo "	$j.	${commits[j]}	${commiters[j]}	" >> "$log_file"
			done
			echo "已找到 $project_path($git_repository_name) 在 $prev_date 的提交记录" >> "$log_file"
			sed -i "s#\(path=\"$project_path\" revision=\"\)[^\"]*\"#\1$last_commit\"#" "$snapshot_file_execute"
			echo -e "\e[32m已替换 $project_path($git_repository_name) 在 $prev_date 的最后一个版本为 $last_commit\e[0m"
			echo "已替换 $project_path($git_repository_name) 在 $prev_date 的最后一个版本为 $last_commit" >> "$log_file"
			replaced_projects["$project_path"]=$last_commit  # 记录已替换的项目路径及对应的最后提交
			echo -e "\033[41;30m<<<<<$project_path($git_repository_name) 基于指定日期 $date 往前遍历完成（截止于：$prev_date）\033[0m"
			echo "<<<<<$project_path($git_repository_name) 基于指定日期 $date 往前遍历完成（截止于：$prev_date）" >> "$log_file"
			break
		else
			echo -e "\e[31m未找到 $project_path($git_repository_name) 在 $prev_date 的提交记录\e[0m"
			echo "未找到 $project_path($git_repository_name) 在 $prev_date 的提交记录" >> "$log_file"
			if [ $i -eq $NUMBER_OF_DAYS_TO_TRAVERSE_FORWARD ]; then
				echo -e "已连续往前查找 $NUMBER_OF_DAYS_TO_TRAVERSE_FORWARD 天没有找到提交记录\n"
				echo "已连续往前查找 $NUMBER_OF_DAYS_TO_TRAVERSE_FORWARD 天没有找到提交记录" >> "$log_file"
				# 如果往前遍历 $NUMBER_OF_DAYS_TO_TRAVERSE_FORWARD 天未找到提交记录，则往后遍历 $NUMBER_OF_DAYS_TO_TRAVERSE_BACKWARD 天
				for ((k = 1; k <= $NUMBER_OF_DAYS_TO_TRAVERSE_BACKWARD; k++)); do
					next_date=$(date -d "$date + $k day" +%Y-%m-%d)
					echo "尝试往后查找 $next_date 的提交记录"
					echo "尝试往后查找 $next_date 的提交记录" >> "$log_file"
					commits=()
					commiters=()
					# 获取提交commit id
					commits=($(git log --since="$(date -d "$next_date - 1 day" +%Y-%m-%d)" --until="$next_date" --pretty=format:"%H"))
					# 获取对应author
					commiters=($(git log --since="$(date -d "$next_date - 1 day" +%Y-%m-%d)" --until="$next_date" --pretty=format:"%an"))
					# 根据commit id进行处理
					if [ ${#commits[@]} -gt 0 ]; then
						last_commit="${commits[0]}"
						# 替换版本号
						echo -e "\e[33m已找到 $project_path($git_repository_name) 在 $next_date 的提交记录如下：\e[0m"
						#echo -e "\e[33m	${commits[@]}\e[0"
						echo -e "\e[33m	打印根据提交时间先后由下到上排序，最上面为最后一笔\e[0m"
						echo "	打印根据提交时间先后由下到上排序，最上面为最后一笔" >> "$log_file"
						echo -e "\e[33m	序号	commit ID					commiter\e[0m"
						echo "	序号	commit ID				commiter" >> "$log_file"
						#for commit in "${commits[@]}"; do
						#	echo -e "\e[33m	$commit\e[0m"
						#	echo "	$commit" >> "$log_file"
						#done
						for ((m=0; m<${#commits[@]}; m++)); do
							echo -e "\e[33m	$m.	${commits[m]}	${commiters[m]}\e[0m"
							echo "	$m.	${commits[m]}	${commiters[m]}" >> "$log_file"
						done
						echo "已找到 $project_path($git_repository_name) 在 $next_date 的提交记录" >> "$log_file"
						sed -i "s#\(path=\"$project_path\" revision=\"\)[^\"]*\"#\1$last_commit\"#" "$snapshot_file_execute"
						echo -e "\e[32m已替换 $project_path($git_repository_name) 在 $next_date 的最后一个版本为 $last_commit\e[0m"
						echo "已替换 $project_path($git_repository_name) 在 $next_date 的最后一个版本为 $last_commit" >> "$log_file"
						replaced_projects["$project_path"]=$last_commit  # 记录已替换的项目路径及对应的最后提交
						echo -e "\033[41;30m<<<<<$project_path($git_repository_name) 基于指定日期 $date 往后遍历完成（截止于：$next_date）\033[0m"
						echo "<<<<<$project_path($git_repository_name) 基于指定日期 $date 往后遍历完成（截止于：$next_date）" >> "$log_file"
						break
					else
						echo -e "\e[31m未找到 $project_path($git_repository_name) 在 $next_date 的提交记录\e[0m"
						echo "未找到 $project_path($git_repository_name) 在 $next_date 的提交记录" >> "$log_file"
						if [ $k -eq $NUMBER_OF_DAYS_TO_TRAVERSE_BACKWARD ]; then
							echo -e "已连续往后查找 $NUMBER_OF_DAYS_TO_TRAVERSE_BACKWARD 天没有找到提交记录"
							echo -e "\033[41;30m<<<<<$project_path($git_repository_name) 基于指定日期 $date 往后遍历完成（截止于：$next_date）\033[0m"
							echo -e "\e[31m没办法！！只能使用模板$snapshot_file 提供的默认revision值：$default_revision\e[0m"
							echo -e "\e[31m请特别留意该目录（仓库）如果使用模板默认revision值是否有影响，可根据需要手动去替换！！\e[0m"
							echo "已连续往后查找 $NUMBER_OF_DAYS_TO_TRAVERSE_BACKWARD 天没有找到提交记录" >> "$log_file"
							echo "<<<<<$project_path($git_repository_name) 基于指定日期 $date 往后遍历完成（截止于：$next_date）" >> "$log_file"
							echo "没办法！！$project_path($git_repository_name) 只能使用模板$snapshot_file 提供的默认revision值：$default_revision" >> "$log_file"
							echo "请特别留意该目录（仓库）如果使用模板默认revision值是否有影响，可根据需要手动去替换！！" >> "$log_file"
						fi
					fi
				done
			fi
		fi
	done
}

sstar_create_snapshot_ergodic_swap()
{
	# 生成时间戳
	timestamp=$(date +"%Y%m%d%H%M%S")

	# 反格式化日期
	target_date=$(sstar_create_snapshot_reformat_date "$date")
	echo "target_date is:$target_date"

	# 备份保留原始的snapshot.xml文件，生成指定日期的目标snapshot文件
	snapshot_target_name="$snapshot_file.t-$target_date.g-$timestamp"
	snapshot_file_execute="$snapshot_target_name.xml"
	cp "$snapshot_file" "$snapshot_file_execute"
	echo "snapshot_file_execute:$snapshot_file_execute"

	# 创建用于记录信息的日志文件
	#log_file="$script_dir/$snapshot_target_name.log"
	log_file="$snapshot_target_name.log"
	echo "log_file is:$log_file"

	# 记录当前目录
	current_dir=$(pwd)

	# 输出当前目录以检查是否正确
	echo "当前目录：$current_dir"

	# 停顿一下方便查看log与snapshot路径等信息是否正确
	sstar_create_snapshot_countdown 5

	# 存储已经替换过的项目路径及对应的最后提交
	declare -A replaced_projects

	# 遍历snapshot.xml文件中的每一行
	while IFS= read -r line; do
		echo -e "\n读取的行：$line" >> "$log_file"
		if [[ "$line" == *"<project"* ]]; then
			# 获取项目信息
			project_path=$(echo "$line" | grep -oP '(?<=path=")[^"]+')

			# 获取仓库名称
			git_repository_name=$(echo "$line" | grep -oP '(?<=name=")[^"]+')

			# 输出当前处理的项目路径
			echo "处理的项目路径：$project_path" >> "$log_file"

			# 检查项目是否已经替换过
			if [[ -n "${replaced_projects[$project_path]}" ]]; then
				echo "项目 $project_path 已经替换过，跳过该项目" >> "$log_file"
				continue
			fi

			# 进入仓库目录
			cd "$project_path" || continue

			# 输出当前所在目录
			echo -e "\n\n当前正在处理的project目录（仓库）：$(pwd) ($git_repository_name) ..."
			echo -e "\n\n当前正在处理的project目录（仓库）：$(pwd) ($git_repository_name) ..." >> "$log_file"

			# >>获取仓库创建时间
			# 检查 .git 目录是否存在
			if [ -d "$(pwd)/.git" ]; then
				# 获取仓库创建时间
				created_timestamp=$(git log --reverse --max-parents=0 --format=%at | tail -n 1)

				# 将创建时间格式化为可读形式
				created_date=$(date -d "@$created_timestamp")

				echo -e "\e[33mThe Git repository in $project_path($git_repository_name) was created on $created_date.\e[0m"
				echo "The Git repository in $project_path($git_repository_name) was created on $created_date." >> "$log_file"

				# 格式化日期为 YYYY-MM-DD
				repository_create_date=$(date -d "@$created_timestamp" +%Y-%m-%d)
				echo -e "\e[33m$project_path($git_repository_name) repository_create_date is: $repository_create_date\e[0m"
				echo "$project_path($git_repository_name) repository_create_date is: $repository_create_date" >> "$log_file"
			else
				echo -e "\e[31mNo Git repository found in $project_path($git_repository_name).\e[0m"
				echo "No Git repository found in $project_path($git_repository_name)." >> "$log_file"
			fi

			# 比较 指定日期 与 仓库创建日期 的先后

			# 将日期转换为时间戳
			timestamp1=$(date -d "$date" +%s)
			timestamp2=$(date -d "$repository_create_date" +%s)

			# 比较时间戳
			if [ "$timestamp1" -lt "$timestamp2" ]; then
				echo -e "\e[31m指定日期：$date 在 仓库创建日期：$repository_create_date 之前！\e[0m"
				echo -e "\e[31m请特别留意xml中该仓库name、path以及revision，可能会导致repo失败！\e[0m"
				echo "指定日期：$date 在 仓库创建日期：$repository_create_date 之前" >> "$log_file"
				echo "请特别留意xml中该仓库name、path以及revision，可能会导致repo失败！" >> "$log_file"
				date_bf_create_flag=1
				if [ "$date_bf_create_flag" -eq 1 ]; then
					echo -e "\e[31m因指定日期还未创建该仓库，使用模板xml提供的默认revision值：$default_revision\e[0m"
					echo -e "\e[31m<<<<<建议手动删除该仓库对应xml中的那一行！！>>>>>\e[0m"
					echo "因指定日期还未创建该仓库，使用模板xml提供的默认revision值：$default_revision" >> "$log_file"
					echo "<<<<<建议手动删除该仓库对应xml中的那一行！！>>>>>" >> "$log_file"
					# do nothing,不做任何替换
					date_bf_create_flag=0
					# 返回到当前目录
					cd "$current_dir" || exit
					continue
				fi
			elif [ "$timestamp1" -gt "$timestamp2" ]; then
				echo -e "\e[32m指定日期：$date 在 仓库创建日期：$repository_create_date 之后\e[0m"
				echo "指定日期：$date 在 仓库创建日期：$repository_create_date 之后" >> "$log_file"
			else
				echo -e "\e[32m指定日期：$date 与 仓库创建日期：$repository_create_date 相同\e[0m"
				echo "指定日期：$date 与 仓库创建日期：$repository_create_date 相同" >> "$log_file"
			fi

			# 获取默认revision值
			default_revision=$(grep -oP "(?<=path=\"$project_path\" revision=\")[^\"]+" "$snapshot_file_execute")

			# 记录信息到日志文件
			echo "项目路径：$project_path"
			echo "项目路径：$project_path" >> "$log_file"
			echo "仓库名称：$git_repository_name"
			echo "仓库名称：$git_repository_name" >> "$log_file"
			echo "默认revision值：$default_revision"
			echo "默认revision值：$default_revision" >> "$log_file"

			# 尝试获取指定日期及之前之后日期的所有提交
			# 尝试获取指定日期
			commits=()
			commiters=()
			# 获取提交commit id
			commits=($(git log --since="$(date -d "$date - 1 day" +%Y-%m-%d)" --until="$date" --pretty=format:"%H"))
			# 获取对应author
			commiters=($(git log --since="$(date -d "$date - 1 day" +%Y-%m-%d)" --until="$date" --pretty=format:"%an"))
			# 根据commit id进行处理
			# 判读数组是不是为空
			if [ ${#commits[@]} -eq 0 ]; then
				#echo "数组为空"
				echo -e "\033[41;30m>>>>>指定日期 $date 的提交信息为空！准备要开始往前往后遍历 ...\033[0m"
				echo ">>>>>指定日期 $date 的提交信息为空！准备要开始往前往后遍历 ..." >> "$log_file"
			else
				#echo "数组不为空"
				# 输出指定日期的提交信息
				echo -e "\033[47;30m指定日期 $date 的提交信息：\033[0m"
				echo "指定日期 $date 的提交信息：" >> "$log_file"
				echo -e "\033[47;30m打印根据提交时间先后由下到上排序，最上面为最后一笔\033[0m"
				echo "	打印根据提交时间先后由下到上排序，最上面为最后一笔" >> "$log_file"
				echo -e "\033[47;30m序号	commit ID					commiter\033[0m"
				echo "序号	commit ID				commiter" >> "$log_file"
				#for commit in "${commits[@]}"; do
				#	#echo "    $commit"
				#	echo -e "\033[47;30m$commit\033[0m"
				#	echo "    $commit" >> "$log_file"
				#done
				for ((i=0; i<${#commits[@]}; i++)); do
					echo -e "\033[47;30m$i.	${commits[i]}	${commiters[i]}\033[0m"
					echo "$i.	${commits[i]}	${commiters[i]}" >> "$log_file"
				done
			fi


			# 如果找到了提交记录
			if [ ${#commits[@]} -gt 0 ]; then
				last_commit="${commits[0]}"
				# 替换版本号
				sed -i "s#\(path=\"$project_path\" revision=\"\)[^\"]*\"#\1$last_commit\"#" "$snapshot_file_execute"
				echo -e "\033[47;30m已替换 $project_path($git_repository_name) 在 $date 的最后一个版本为 $last_commit\033[0m"
				replaced_projects["$project_path"]=$last_commit  # 记录已替换的项目路径及对应的最后提交

				# 记录信息到日志文件
				echo "已替换 $project_path($git_repository_name) 在 $date 的最后一个版本为 $last_commit" >> "$log_file"
			else
				echo -e "\e[31m未找到 $project_path($git_repository_name) 在指定日期 $date 的提交记录\e[0m"
				echo "未找到 $project_path($git_repository_name) 在指定日期 $date 的提交记录" >> "$log_file"

				# 尝试获取指定日期之前之后日期的所有提交
				sstar_create_snapshot_ergodic_process
			fi

			# 返回到当前目录
			cd "$current_dir" || exit
		fi
	done < "$snapshot_file_execute"
}

sstar_create_snapshot_finished_info()
{
	echo -e "\n"
	echo -e "\033[42;30m处理完成,版本xml已保存为：$snapshot_file_execute\033[0m"
	echo -e "\033[42;30m过程记录信息已保存到文件：$log_file\033[0m"

	echo -e "\n以下是repo切换到指定snapshot的方法,供参考：
=================================================================================
case 1. 在本地已有alkaid目录中切换
	cd alkaid
	repo forall -c "git reset --hard HEAD"
	repo forall -c "git clean -df"
	cp alkaid_snapshot.xml ./.repo/manifests/
	repo init -m alkaid_snapshot.xml
	repo sync -c -j8  (可以根据需要添加 --no-tags)

case 2. 新建alkaid_dbg目录重新repo init到指定snapshot
	mkdir alkaid_dbg;cd alkaid_dbg
	将alkaid_snapshot.xml拷贝到当前目录alkaid_dbg
	mkdir -p .repo/manifests
	chmod 755 alkaid_snapshot.xml
	mv alkaid_snapshot.xml .repo/manifests/
	repo init -u http://hcgit04:9080/manifest/alkaid -m alkaid_snapshot.xml
	repo sync -c -j8  (可以根据需要添加 --no-tags)
=================================================================================
"
}

#run func
sstar_create_snapshot_check_alkaid_path
sstar_create_snapshot_input_param_chk $1 $2
sstar_create_snapshot_ergodic_swap
sstar_create_snapshot_finished_info
