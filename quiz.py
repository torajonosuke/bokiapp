import random
from itertools import permutations
from pathlib import Path

import pandas as pd


base_dir = Path(__file__).resolve().parent
file_path = base_dir / "material_boki3.xlsx"


# =========================
# 分類問題
# =========================
df_class = pd.read_excel(file_path, sheet_name="分類問題")

current_stage = 2  # ← クラスごとに変える

df_class = df_class[df_class["stage"] <= current_stage]

classification_questions = []

for _, row in df_class.iterrows():
    question = {
        "question": f"{row['account_name']}はどの分類？",
        "choices": [
            ("1", "資産"),
            ("2", "負債"),
            ("3", "資本"),
            ("4", "収益"),
            ("5", "費用")
        ],
        "answer": str(row["answer_value"]),
        "explanation": row["explanation"]
    }
    classification_questions.append(question)


# =========================
# 勘定科目逆引き問題
# =========================
reverse_questions = []

account_choices = df_class["account_name"].dropna().tolist()

for _, row in df_class.iterrows():
    correct = row["account_name"]

    wrong_choices = [x for x in account_choices if x != correct]

    # 選択肢が足りないと random.sample でエラーになるので保険
    if len(wrong_choices) >= 3:
        sampled_wrong = random.sample(wrong_choices, 3)
    else:
        sampled_wrong = wrong_choices

    choices = sampled_wrong + [correct]
    random.shuffle(choices)

    question = {
        "question": row["explanation"],
        "choices": [(str(i + 1), choice) for i, choice in enumerate(choices)],
        "answer": str(choices.index(correct) + 1),
        "explanation": f"正解は「{correct}」です。"
    }
    reverse_questions.append(question)

# =========================
# 理由問題
# =========================
df = pd.read_excel(file_path, sheet_name="理由問題")

current_stage = 3  # ← ここだけ変える

df = df[df["stage"] <= current_stage]

reason_questions = []
for _, row in df.iterrows():
    question = {
        "question": row["question"],
        "choices": [
            ("1", row["choice1"]),
            ("2", row["choice2"]),
            ("3", row["choice3"]),
            ("4", row["choice4"])
        ],
        "answer": str(row["answer"]),
        "explanation": row["explanation"]
    }
    reason_questions.append(question)

# =========================
# 仕訳問題
# =========================
df_journal = pd.read_excel(file_path, sheet_name="journal")

journal_questions = []

for _, row in df_journal.iterrows():
    question = {
        "question": row["question"],
        "choices": [
            ("1", row["choice1"]),
            ("2", row["choice2"]),
            ("3", row["choice3"]),
            ("4", row["choice4"])
        ],
        "answer": str(row["answer"]),
        "explanation": row["explanation"],
        "level": int(row["level"])
    }
    journal_questions.append(question)

def split_choices(value):
    if value is None:
        return []

    text = str(value).strip()

    if text == "" or text.lower() == "nan":
        return []

    return [item.strip() for item in text.split(",") if item.strip()]

# =========================
# 入力式仕訳
# =========================
df_journal_input = pd.read_excel(file_path, sheet_name="journal_input")

journal_input_questions = []

for _, row in df_journal_input.iterrows():
    question = {
        "question": row["question"],

        "debit1_choices": split_choices(row["debit1_choices"]),
        "debit1_answer": row["debit1_answer"],
        "debit1_amount": row["debit1_amount"],

        "credit1_choices": split_choices(row["credit1_choices"]),
        "credit1_answer": row["credit1_answer"],
        "credit1_amount": row["credit1_amount"],

        "debit2_choices": split_choices(row["debit2_choices"]),
        "debit2_answer": row["debit2_answer"],
        "debit2_amount": row["debit2_amount"],

        "credit2_choices": split_choices(row["credit2_choices"]),
        "credit2_answer": row["credit2_answer"],
        "credit2_amount": row["credit2_amount"],

        "explanation": row["explanation"]
    }

    journal_input_questions.append(question)



def get_question_pool(mode):
    if mode == "reason":
        return reason_questions
    elif mode == "reverse":
        return reverse_questions
    elif mode == "journal":
        return journal_questions
    elif mode == "journal_easy":
        return [q for q in journal_questions if q["level"] == 1]
    elif mode == "journal_hard":
        return [q for q in journal_questions if q["level"] >= 2]
    elif mode == "journal_input":
        return journal_input_questions
    elif mode == "ledger":
        return make_ledger_questions_from_journal_input()
    elif mode == "stock_flow":
        return stock_flow_questions
    elif mode == "trial_balance_direction":
        return trial_balance_direction_questions
    elif mode == "trial_balance_amount":
        return trial_balance_amount_questions
    elif mode == "inventory_gap":
        return inventory_gap_questions
    elif mode == "inventory_journal_link":
        return inventory_journal_link_questions
    elif mode == "closing_transfer":
        return closing_transfer_questions
    elif mode == "bs_pl":
        return bs_pl_questions
    elif mode == "bs_pl_reason":
        return bs_pl_reason_questions
    elif mode == "bs_pl_reverse":
        return bs_pl_reverse_questions
    elif mode == "worksheet_intro":
        return worksheet_intro_questions
    elif mode == "bs_or_pl":
        return bs_or_pl_questions
    elif mode == "worksheet_sort":
        return worksheet_sort_questions
    elif mode == "worksheet_amount":
        return worksheet_amount_questions
    elif mode == "adjustment_reason":
        return adjustment_reason_questions
    elif mode == "adjustment_journal":
        return adjustment_journal_questions
    elif mode == "worksheet_flow":
        return worksheet_flow_questions
    elif mode == "worksheet_to_fs":
        return worksheet_to_fs_questions
    elif mode == "mini_closing":
        return mini_closing_questions
    else:
        return classification_questions

def get_review_questions(mode, wrong_question_texts):
    pool = get_question_pool(mode)

    normalized_wrong_texts = [text.replace(" ", "").replace("　", "") for text in wrong_question_texts]

    return [
        q for q in pool
        if q["question"].replace(" ", "").replace("　", "") in normalized_wrong_texts
    ]

def get_questions_with_indices(mode, num_questions):
    pool = get_question_pool(mode)
    count = min(num_questions, len(pool))
    indices = random.sample(range(len(pool)), count)
    selected = [pool[i] for i in indices]
    return selected, indices

def get_questions_by_indices(mode, indices):
    pool = get_question_pool(mode)
    return [pool[i] for i in indices if 0 <= i < len(pool)]# 出題取得
# =========================
def get_questions(mode, num_questions):
    selected, _ = get_questions_with_indices(mode, num_questions)
    return selected

# =========================
# 通常問題の採点
# =========================
def grade_answers(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        user = form.get(f"q{i}")
        answer = form.get(f"a{i}")
        explanation = form.get(f"e{i}")
        question = form.get(f"text{i}")

        user_label = form.get(f"label_{i}_{user}") if user else "未回答"
        answer_label = form.get(f"label_{i}_{answer}")

        is_correct = (user == answer)
        if is_correct:
            score += 1

        results.append({
            "question": question,
            "user_answer": user_label,
            "correct_answer": answer_label,
            "explanation": explanation,
            "is_correct": is_correct
        })

    return score, results


# =========================
# 入力式仕訳 採点補助
# =========================
def normalize_text(value):
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() == "nan":
        return ""

    return text


def normalize_amount(value):
    if value is None:
        return ""

    text = str(value).replace(",", "").strip()

    if text == "" or text == "-":
        return ""

    if text.lower() == "nan":
        return ""

    if text.endswith(".0"):
        text = text[:-2]

    return text

def score_pair(user_row, correct_row):
    """
    1行分の採点
    科目一致: 0.5点
    金額一致: 0.5点
    """
    subject_ok = (user_row["subject"] == correct_row["subject"])
    amount_ok = (user_row["amount"] == correct_row["amount"])

    score = 0
    if subject_ok:
        score += 0.5
    if amount_ok:
        score += 0.5

    return score, subject_ok, amount_ok


def evaluate_side(user_rows, correct_rows, side_name):
    """
    借方 or 貸方を順不同で採点する
    """
    # 正解側で空行は除外
    correct_rows = [
        row for row in correct_rows
        if not (row["subject"] == "" and row["amount"] == "")
    ]

    # ユーザー側も完全空行は除外
    user_rows = [
        row for row in user_rows
        if not (row["subject"] == "" and row["amount"] == "")
    ]

    question_max = len(correct_rows)
    best_score = -1
    best_details = []

    # 正解が0行なら採点対象なし
    if question_max == 0:
        return 0, 0, []

    # ユーザー行数が足りない場合は空行で埋める
    while len(user_rows) < len(correct_rows):
        user_rows.append({"subject": "", "amount": ""})

    # ユーザー行が多い場合は、先頭から正解数分だけ採点対象
    user_rows = user_rows[:len(correct_rows)]

    # 順不同対応：並び替えの中で最高得点になる組み合わせを採用
    for perm in permutations(user_rows, len(correct_rows)):
        current_score = 0
        current_details = []

        for i, correct_row in enumerate(correct_rows):
            user_row = perm[i]
            row_score, subject_ok, amount_ok = score_pair(user_row, correct_row)
            current_score += row_score

            if subject_ok and amount_ok:
                feedback = "科目と金額は正しいです"
            elif subject_ok and not amount_ok:
                feedback = "科目は正しいですが、金額が違います"
            elif not subject_ok and amount_ok:
                feedback = "金額は正しいですが、科目が違います"
            else:
                feedback = "科目と金額の両方が違います"

            current_details.append({
                "row_name": f"{side_name}{i+1}",
                "index": i,
                "user_subject": user_row["subject"],
                "user_amount": user_row["amount"],
                "correct_subject": correct_row["subject"],
                "correct_amount": correct_row["amount"],
                "subject_ok": subject_ok,
                "amount_ok": amount_ok,
                "row_score": row_score,
                "feedback": feedback
            })

        if current_score > best_score:
            best_score = current_score
            best_details = current_details.copy()

    return best_score, question_max, best_details


# =========================
# 入力式仕訳の採点
# =========================
def grade_journal_input(form, num_questions, questions):
    total_score = 0
    results = []

    for i in range(num_questions):
        q = questions[i]

        user_answer = {
            "debit1": normalize_text(form.get(f"debit1_{i}")),
            "debit1_amount": normalize_amount(form.get(f"debit1_amount_{i}")),
            "debit2": normalize_text(form.get(f"debit2_{i}")),
            "debit2_amount": normalize_amount(form.get(f"debit2_amount_{i}")),
            "credit1": normalize_text(form.get(f"credit1_{i}")),
            "credit1_amount": normalize_amount(form.get(f"credit1_amount_{i}")),
            "credit2": normalize_text(form.get(f"credit2_{i}")),
            "credit2_amount": normalize_amount(form.get(f"credit2_amount_{i}")),
        }

        correct_answer = {
            "debit1": normalize_text(q.get("debit1_answer")),
            "debit1_amount": normalize_amount(q.get("debit1_amount")),
            "debit2": normalize_text(q.get("debit2_answer")),
            "debit2_amount": normalize_amount(q.get("debit2_amount")),
            "credit1": normalize_text(q.get("credit1_answer")),
            "credit1_amount": normalize_amount(q.get("credit1_amount")),
            "credit2": normalize_text(q.get("credit2_answer")),
            "credit2_amount": normalize_amount(q.get("credit2_amount")),
        }

        user_debit_rows = [
            {"subject": user_answer["debit1"], "amount": user_answer["debit1_amount"]},
            {"subject": user_answer["debit2"], "amount": user_answer["debit2_amount"]},
        ]
        correct_debit_rows = [
            {"subject": correct_answer["debit1"], "amount": correct_answer["debit1_amount"]},
            {"subject": correct_answer["debit2"], "amount": correct_answer["debit2_amount"]},
        ]

        user_credit_rows = [
            {"subject": user_answer["credit1"], "amount": user_answer["credit1_amount"]},
            {"subject": user_answer["credit2"], "amount": user_answer["credit2_amount"]},
        ]
        correct_credit_rows = [
            {"subject": correct_answer["credit1"], "amount": correct_answer["credit1_amount"]},
            {"subject": correct_answer["credit2"], "amount": correct_answer["credit2_amount"]},
        ]

        debit_score, debit_max, debit_details = evaluate_side(
            user_debit_rows, correct_debit_rows, "借方"
        )
        credit_score, credit_max, credit_details = evaluate_side(
            user_credit_rows, correct_credit_rows, "貸方"
        )

        question_score = debit_score + credit_score
        question_max = debit_max + credit_max
        is_correct = (question_score == question_max)

        total_score += question_score

        results.append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": q.get("explanation", ""),
            "is_correct": is_correct,
            "question_score": question_score,
            "question_max": question_max,
            "row_details": debit_details + credit_details
        })

    return total_score, results


def label_from_value(value, mode):
    labels = {
        "1": "資産",
        "2": "負債",
        "3": "資本",
        "4": "収益",
        "5": "費用"
    }
    return labels.get(value, value)

def make_ledger_questions_from_journal_input():
    ledger_questions = []

    for q in journal_input_questions:
        entries = []

        if normalize_text(q.get("debit1_answer")):
            entries.append({
                "account": normalize_text(q.get("debit1_answer")),
                "side": "借方",
                "amount": normalize_amount(q.get("debit1_amount"))
            })

        if normalize_text(q.get("debit2_answer")):
            entries.append({
                "account": normalize_text(q.get("debit2_answer")),
                "side": "借方",
                "amount": normalize_amount(q.get("debit2_amount"))
            })

        if normalize_text(q.get("credit1_answer")):
            entries.append({
                "account": normalize_text(q.get("credit1_answer")),
                "side": "貸方",
                "amount": normalize_amount(q.get("credit1_amount"))
            })

        if normalize_text(q.get("credit2_answer")):
            entries.append({
                "account": normalize_text(q.get("credit2_answer")),
                "side": "貸方",
                "amount": normalize_amount(q.get("credit2_amount"))
            })

        account_choices = []
        for entry in entries:
            if entry["account"] not in account_choices:
                account_choices.append(entry["account"])

        ledger_question = {
            "question": q["question"],
            "entries": entries,
            "account_choices": account_choices,
            "explanation": normalize_text(q.get("explanation"))
        }
        ledger_questions.append(ledger_question)

    return ledger_questions

def grade_ledger_answers(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        question = form.get(f"ledger_question_{i}")
        explanation = form.get(f"ledger_explanation_{i}")
        entry_count = int(form.get(f"ledger_entry_count_{i}", 0))

        row_results = []
        question_score = 0

        for j in range(entry_count):
            user_account = normalize_text(form.get(f"ledger_account_{i}_{j}"))
            user_side = normalize_text(form.get(f"ledger_side_{i}_{j}"))

            correct_account = normalize_text(form.get(f"ledger_account_answer_{i}_{j}"))
            correct_side = normalize_text(form.get(f"ledger_side_answer_{i}_{j}"))
            amount = normalize_amount(form.get(f"ledger_amount_{i}_{j}"))

            account_ok = (user_account == correct_account)
            side_ok = (user_side == correct_side)

            row_score = 0
            if account_ok:
                row_score += 0.5
            if side_ok:
                row_score += 0.5

            # ① 先にカテゴリを決める
            if account_ok and side_ok:
                category = "正解"
            elif account_ok and not side_ok:
                category = "方向ミス"
            elif not account_ok and side_ok:
                category = "勘定ミス"
            else:
                category = "両方ミス"

            # ② そのあとフィードバックを作る
            if account_ok and side_ok:
                feedback = f"{correct_account}勘定の{correct_side}に正しく転記できています。仕訳の{correct_side}は元帳の{correct_side}に書きます。"

            elif account_ok and not side_ok:
                if user_side:
                    feedback = f"{correct_account}勘定までは正しいですが、借方・貸方が逆です。仕訳の{correct_side}は元帳の{correct_side}にそのまま転記します。"
                else:
                    feedback = f"{correct_account}勘定までは正しいですが、借方・貸方が未選択です。仕訳の{correct_side}は元帳の{correct_side}に書きます。"

            elif not account_ok and side_ok:
                if user_account:
                    feedback = f"{correct_side}である点は正しいですが、勘定が違います。この行は{correct_account}勘定に転記します。"
                else:
                    feedback = f"{correct_side}である点は正しいですが、勘定名が未選択です。この行は{correct_account}勘定に転記します。"

            else:
                if not user_account and not user_side:
                    feedback = f"勘定名も借方・貸方も未選択です。この行は{correct_account}勘定の{correct_side}に転記します。"
                elif not user_account:
                    feedback = f"借方・貸方は{user_side}を選んでいますが、勘定名が未選択です。この行は{correct_account}勘定の{correct_side}に転記します。"
                elif not user_side:
                    feedback = f"{user_account}勘定を選んでいますが、借方・貸方が未選択です。この行は{correct_account}勘定の{correct_side}に転記します。"
                else:
                    feedback = f"勘定名と借方・貸方の両方が違います。この行は{correct_account}勘定の{correct_side}に転記します。"

            question_score += row_score

            row_results.append({
                "account": correct_account,
                "amount": amount,
                "user_account": user_account,
                "user_side": user_side,
                "correct_account": correct_account,
                "correct_side": correct_side,
                "account_ok": account_ok,
                "side_ok": side_ok,
                "row_score": row_score,
                "feedback": f"【{category}】" + feedback
                
            })

        question_max = entry_count
        is_correct = (question_score == question_max)
        score += question_score

        results.append({
            "question": question,
            "row_results": row_results,
            "question_score": question_score,
            "question_max": question_max,
            "explanation": explanation,
            "is_correct": is_correct
        })

    return score, results

def get_account_only_questions(num_questions):
    pool = journal_input_questions
    count = min(num_questions, len(pool))
    selected = random.sample(pool, count)

    all_accounts = set()
    for q in pool:
        for key in ["debit1_answer", "debit2_answer", "credit1_answer", "credit2_answer"]:
            account = normalize_text(q.get(key))
            if account:
                all_accounts.add(account)

    all_accounts = list(all_accounts)

    results = []

    for q in selected:
        correct_accounts = []

        for key in ["debit1_answer", "debit2_answer", "credit1_answer", "credit2_answer"]:
            account = normalize_text(q.get(key))
            if account and account not in correct_accounts:
                correct_accounts.append(account)

        wrong_candidates = [a for a in all_accounts if a not in correct_accounts]
        wrong_count = max(0, 4 - len(correct_accounts))
        sampled_wrong = random.sample(wrong_candidates, min(wrong_count, len(wrong_candidates)))

        choices = correct_accounts + sampled_wrong
        random.shuffle(choices)

        results.append({
            "question": q["question"],
            "choices": choices,
            "answers": correct_accounts,
            "explanation": normalize_text(q.get("explanation"))
        })

    return results

def grade_account_only(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        user_answers = form.getlist(f"q{i}")
        correct_answers = form.get(f"answers{i}", "").split(",")

        user_set = set(user_answers)
        correct_set = set(correct_answers)

        is_correct = user_set == correct_set

        if is_correct:
            score += 1

        results.append({
            "question": f"問題{i+1}",
            "user_answer": ", ".join(user_answers) if user_answers else "未回答",
            "correct_answer": ", ".join(correct_answers),
            "explanation": "",
            "is_correct": is_correct
        })

    return score, results

def get_direction_only_questions(num_questions):
    pool = journal_input_questions
    count = min(num_questions, len(pool))
    selected = random.sample(pool, count)

    results = []

    for q in selected:
        entries = []

        if normalize_text(q.get("debit1_answer")):
            entries.append({
                "account": normalize_text(q.get("debit1_answer")),
                "side": "借方"
            })

        if normalize_text(q.get("debit2_answer")):
            entries.append({
                "account": normalize_text(q.get("debit2_answer")),
                "side": "借方"
            })

        if normalize_text(q.get("credit1_answer")):
            entries.append({
                "account": normalize_text(q.get("credit1_answer")),
                "side": "貸方"
            })

        if normalize_text(q.get("credit2_answer")):
            entries.append({
                "account": normalize_text(q.get("credit2_answer")),
                "side": "貸方"
            })

        results.append({
            "question": q["question"],
            "entries": entries,
            "explanation":normalize_text(q.get("explanation"))
        })

    return results

def grade_direction_only(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        question = form.get(f"direction_question_{i}")
        explanation = form.get(f"direction_explanation_{i}")
        entry_count = int(form.get(f"direction_entry_count_{i}", 0))

        row_results = []
        question_score = 0

        for j in range(entry_count):
            account = normalize_text(form.get(f"direction_account_{i}_{j}"))
            correct_side = normalize_text(form.get(f"direction_side_answer_{i}_{j}"))
            user_side = normalize_text(form.get(f"direction_side_{i}_{j}"))

            side_ok = (user_side == correct_side)

            if side_ok:
                question_score += 1
                feedback = f"{account}は{correct_side}で正しいです。"
            else:
                if user_side:
                    feedback = f"{account}は{user_side}ではなく、{correct_side}です。"
                else:
                    feedback = f"{account}の方向が未選択です。正解は{correct_side}です。"

            row_results.append({
                "account": account,
                "user_side": user_side,
                "correct_side": correct_side,
                "side_ok": side_ok,
                "feedback": feedback
            })

        score += question_score

        results.append({
            "question": question,
            "row_results": row_results,
            "question_score": question_score,
            "question_max": entry_count,
            "explanation": explanation,
            "is_correct": (question_score == entry_count)
        })

    return score, results

# =========================
# 残高試算表（方向だけ）
# =========================
trial_balance_direction_questions = [
    {"account": "現金", "answer": "借方", "explanation": "現金は資産なので、残高は借方に出ます。"},
    {"account": "普通預金", "answer": "借方", "explanation": "普通預金は資産なので、残高は借方に出ます。"},
    {"account": "売掛金", "answer": "借方", "explanation": "売掛金は資産なので、残高は借方に出ます。"},
    {"account": "受取手形", "answer": "借方", "explanation": "受取手形は資産なので、残高は借方に出ます。"},
    {"account": "繰越商品", "answer": "借方", "explanation": "繰越商品は資産なので、残高は借方に出ます。"},
    {"account": "備品", "answer": "借方", "explanation": "備品は資産なので、残高は借方に出ます。"},
    {"account": "前払費用", "answer": "借方", "explanation": "前払費用は資産なので、残高は借方に出ます。"},
    {"account": "貸付金", "answer": "借方", "explanation": "貸付金は資産なので、残高は借方に出ます。"},
    {"account": "買掛金", "answer": "貸方", "explanation": "買掛金は負債なので、残高は貸方に出ます。"},
    {"account": "支払手形", "answer": "貸方", "explanation": "支払手形は負債なので、残高は貸方に出ます。"},
    {"account": "借入金", "answer": "貸方", "explanation": "借入金は負債なので、残高は貸方に出ます。"},
    {"account": "未払金", "answer": "貸方", "explanation": "未払金は負債なので、残高は貸方に出ます。"},
    {"account": "前受金", "answer": "貸方", "explanation": "前受金は負債なので、残高は貸方に出ます。"},
    {"account": "資本金", "answer": "貸方", "explanation": "資本金は純資産なので、残高は貸方に出ます。"},
    {"account": "売上", "answer": "貸方", "explanation": "売上は収益なので、残高は貸方に出ます。"},
    {"account": "受取利息", "answer": "貸方", "explanation": "受取利息は収益なので、残高は貸方に出ます。"},
    {"account": "仕入", "answer": "借方", "explanation": "仕入は費用なので、残高は借方に出ます。"},
    {"account": "給料", "answer": "借方", "explanation": "給料は費用なので、残高は借方に出ます。"},
    {"account": "水道光熱費", "answer": "借方", "explanation": "水道光熱費は費用なので、残高は借方に出ます。"},
    {"account": "支払家賃", "answer": "借方", "explanation": "支払家賃は費用なので、残高は借方に出ます。"},
    {"account": "支払利息", "answer": "借方", "explanation": "支払利息は費用なので、残高は借方に出ます。"},
]

def get_trial_balance_direction_questions(num_questions):
    count = min(num_questions, len(trial_balance_direction_questions))
    selected = random.sample(trial_balance_direction_questions, count)
    return selected

# ① 残高の方向
def grade_trial_balance_direction(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        account = form.get(f"tb_account_{i}")
        user = form.get(f"tb_side_{i}", "")
        answer = form.get(f"tb_answer_{i}", "")
        explanation = form.get(f"tb_explanation_{i}", "")

        is_correct = (user == answer)
        if is_correct:
            score += 1

        results.append({
            "question": f"{account}の残高は借方・貸方どちら？",
            "account": account,
            "user_side": user or "未選択",
            "correct_side": answer,
            "explanation": explanation,
            "is_correct": is_correct
        })

    return score, results


def grade_trial_balance_amount(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        account = normalize_text(form.get(f"tb_amount_account_{i}"))
        side = normalize_text(form.get(f"tb_amount_side_{i}"))
        user_amount = normalize_amount(form.get(f"tb_amount_user_{i}"))
        correct_amount = normalize_amount(form.get(f"tb_amount_answer_{i}"))
        explanation = normalize_text(form.get(f"tb_amount_explanation_{i}"))

        is_correct = (user_amount == correct_amount)
        if is_correct:
            score += 1

        if user_amount == "":
            feedback = f"{account}の残高が未入力です。正解は{correct_amount}です。"
        elif is_correct:
            feedback = f"{account}の残高は{correct_amount}で正しいです。"
        else:
            feedback = f"{account}の残高は{user_amount}ではなく、{correct_amount}です。"

        results.append({
            "question": f"{account}の残高はいくら？",
            "account": account,
            "side": side,
            "user_amount": user_amount or "未入力",
            "correct_amount": correct_amount,
            "feedback": feedback,
            "explanation": explanation,
            "is_correct": is_correct
        })

    return score, results

# =========================
# 残高試算表（残高入力）
# =========================
trial_balance_amount_questions = [
    {"account": "現金", "side": "借方", "amount": "300000", "explanation": "現金は資産なので、残高は借方に300,000です。"},
    {"account": "普通預金", "side": "借方", "amount": "450000", "explanation": "普通預金は資産なので、残高は借方に450,000です。"},
    {"account": "売掛金", "side": "借方", "amount": "120000", "explanation": "売掛金は資産なので、残高は借方に120,000です。"},
    {"account": "受取手形", "side": "借方", "amount": "80000", "explanation": "受取手形は資産なので、残高は借方に80,000です。"},
    {"account": "繰越商品", "side": "借方", "amount": "200000", "explanation": "繰越商品は資産なので、残高は借方に200,000です。"},
    {"account": "備品", "side": "借方", "amount": "150000", "explanation": "備品は資産なので、残高は借方に150,000です。"},
    {"account": "買掛金", "side": "貸方", "amount": "180000", "explanation": "買掛金は負債なので、残高は貸方に180,000です。"},
    {"account": "支払手形", "side": "貸方", "amount": "90000", "explanation": "支払手形は負債なので、残高は貸方に90,000です。"},
    {"account": "借入金", "side": "貸方", "amount": "500000", "explanation": "借入金は負債なので、残高は貸方に500,000です。"},
    {"account": "未払金", "side": "貸方", "amount": "70000", "explanation": "未払金は負債なので、残高は貸方に70,000です。"},
    {"account": "資本金", "side": "貸方", "amount": "1000000", "explanation": "資本金は純資産なので、残高は貸方に1,000,000です。"},
    {"account": "売上", "side": "貸方", "amount": "600000", "explanation": "売上は収益なので、残高は貸方に600,000です。"},
    {"account": "受取利息", "side": "貸方", "amount": "5000", "explanation": "受取利息は収益なので、残高は貸方に5,000です。"},
    {"account": "仕入", "side": "借方", "amount": "400000", "explanation": "仕入は費用なので、残高は借方に400,000です。"},
    {"account": "給料", "side": "借方", "amount": "120000", "explanation": "給料は費用なので、残高は借方に120,000です。"},
    {"account": "水道光熱費", "side": "借方", "amount": "30000", "explanation": "水道光熱費は費用なので、残高は借方に30,000です。"},
    {"account": "支払家賃", "side": "借方", "amount": "60000", "explanation": "支払家賃は費用なので、残高は借方に60,000です。"},
    {"account": "支払利息", "side": "借方", "amount": "10000", "explanation": "支払利息は費用なので、残高は借方に10,000です。"},
]

def get_trial_balance_amount_questions(num_questions):
    count = min(num_questions, len(trial_balance_amount_questions))
    selected = random.sample(trial_balance_amount_questions, count)
    return selected

def grade_trial_balance_amount(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        account = normalize_text(form.get(f"tb_amount_account_{i}"))
        side = normalize_text(form.get(f"tb_amount_side_{i}"))
        user_amount = normalize_amount(form.get(f"tb_amount_user_{i}"))
        correct_amount = normalize_amount(form.get(f"tb_amount_answer_{i}"))
        explanation = normalize_text(form.get(f"tb_amount_explanation_{i}"))

        is_correct = (user_amount == correct_amount)
        if is_correct:
            score += 1

        if user_amount == "":
            feedback = f"{account}の残高が未入力です。正解は{correct_amount}です。"
        elif is_correct:
            feedback = f"{account}の残高は{correct_amount}で正しいです。"
        else:
            feedback = f"{account}の残高は{user_amount}ではなく、{correct_amount}です。"

        results.append({
            "account": account,
            "side": side,
            "user_amount": user_amount,
            "correct_amount": correct_amount,
            "feedback": feedback,
            "explanation": explanation,
            "is_correct": is_correct
        })

    return score, results


def get_questions_with_indices(mode, num_questions):
    pool = get_question_pool(mode)
    count = min(num_questions, len(pool))
    indices = random.sample(range(len(pool)), count)
    selected = [pool[i] for i in indices]
    return selected, indices

# =========================
# ストック・フロー問題
# 「ストック/フロー」ではなく
# 「引き継ぐ / リセットされる」で問う
# =========================
stock_flow_questions = [
    {
        "question": "現金は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "carry",
        "explanation": "現金は、次年度へ継がれます（引き継ぐ＝ストック）。"
    },
    {
        "question": "建物は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "carry",
        "explanation": "建物は、次年度へ引き継がれます（引き継ぐ＝ストック）。"
    },
    {
        "question": "売掛金は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "carry",
        "explanation": "売掛金は、次年度へ引き継がれます（引き継ぐ＝ストック）。"
    },
    {
        "question": "買掛金は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "carry",
        "explanation": "買掛金は、次年度へ引き継がれます（引き継ぐ＝ストック）。"
    },
    {
        "question": "資本金は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "carry",
        "explanation": "資本金は、次年度へ引き継がれます（引き継ぐ＝ストック）。"
    },
    {
        "question": "売上は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "reset",
        "explanation": "売上は、期末にリセットされます（リセット＝フロー）。"
    },
    {
        "question": "受取利息は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "reset",
        "explanation": "受取利息は、期末にリセットされます（リセット＝フロー）。"
    },
    {
        "question": "仕入は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "reset",
        "explanation": "仕入は、期末にリセットされます（リセット＝フロー）。"
    },
    {
        "question": "給料は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "reset",
        "explanation": "給料は、期末にリセットされます（リセット＝フロー）。"
    },
    {
        "question": "水道光熱費は、期末に次年度へ引き継がれる？それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
        ],
        "answer": "reset",
        "explanation": "水道光熱費は、期末にリセットされます（リセット＝フロー）。"
    },
    {
        "question": "通信費は、期末に次年度へ引き継がれる？ それともリセットされる？",
        "choices": [
            ("carry", "引き継がれる"),
            ("reset", "リセットされる")
    ],
    "answer": "reset",
    "explanation": "通信費は、期末にリセットされます（リセット＝フロー）。"
    }
]

inventory_gap_questions = [
    {
        "question": "100個仕入れて90個売れた。仕入100を全部費用にしてよい？",
        "choices": [
            ("yes", "はい"),
            ("no", "いいえ")
        ],
        "answer": "no",
        "explanation": "10個残っているため、すべてを費用にすることはできません。"
    },
    {
        "question": "残っている10個の商品は何になる？",
        "choices": [
            ("expense", "費用"),
            ("asset", "資産")
        ],
        "answer": "asset",
        "explanation": "まだ会社に残っているので資産です。"
    },
    {
        "question": "残りの商品はどう処理する？",
        "choices": [
            ("expense", "そのまま費用にする"),
            ("asset", "資産に戻す")
        ],
        "answer": "asset",
        "explanation": "費用にしすぎているため、資産に戻します。"
    }
]

inventory_journal_link_questions = [
    {
        "question": "100個仕入れて90個売れた。残りの商品を資産に戻す仕訳は？",
        "choices": [
            ("correct", "繰越商品 / 仕入"),
            ("reverse", "仕入 / 繰越商品"),
            ("wrong1", "現金 / 仕入"),
            ("wrong2", "仕入 / 現金")
        ],
        "answer": "correct",
        "explanation": "残っている商品は資産として繰越商品にし、費用である仕入を減らします。"
    },
    {
        "question": "なぜこの仕訳になる？",
        "choices": [
            ("increase", "費用を増やすため"),
            ("decrease", "費用を減らすため"),
            ("asset_down", "資産を減らすため")
        ],
        "answer": "decrease",
        "explanation": "費用にしすぎている仕入を減らすためです。"
    }
]

closing_transfer_questions = [
    {
        "question": "なぜ収益や費用は期末にゼロにするのか？",
        "choices": [
            ("wrong1", "現金に変えるため"),
            ("correct", "次の期間に持ち越さないため"),
            ("wrong2", "資産にするため")
        ],
        "answer": "correct",
        "explanation": "収益や費用はフローなので、期末にリセットする必要があります。"
    },
    {
        "question": "収益や費用の結果はどこに集める？",
        "choices": [
            ("wrong1", "現金"),
            ("correct", "損益"),
            ("wrong2", "売上")
        ],
        "answer": "correct",
        "explanation": "収益と費用は損益勘定に集めて結果を計算します。"
    },
    {
        "question": "売上100,000を損益に振り替える仕訳は？",
        "choices": [
            ("correct", "売上 / 損益"),
            ("wrong1", "損益 / 売上"),
            ("wrong2", "現金 / 売上")
        ],
        "answer": "correct",
        "explanation": "収益は貸方にあるため、借方に移してゼロにします。"
    },
    {
        "question": "仕入50,000を損益に振り替える仕訳は？",
        "choices": [
            ("correct", "損益 / 仕入"),
            ("wrong1", "仕入 / 損益"),
            ("wrong2", "現金 / 仕入")
        ],
        "answer": "correct",
        "explanation": "費用は借方にあるため、貸方に移してゼロにします。"
    }
]

bs_pl_questions = [
    {
    "question": "売上は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "pl",
    "explanation": "売上はリセットされるためフローです（フロー＝PL）。"
    },
    {
    "question": "給料は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "pl",
    "explanation": "給料はリセットされるためフローです（フロー＝PL）。"
    },
    {
    "question": "仕入は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "pl",
    "explanation": "仕入はリセットされるためフローです（フロー＝PL）。"
    },
    {
    "question": "現金は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "bs",
    "explanation": "現金は引き継がれるためストックです（ストックー＝BS）。"
    },
    {
    "question": "売掛金は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "bs",
    "explanation": "売掛金は引き継がれるためストックです（ストックー＝BS）。"
    },
    {
    "question": "買掛金は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "bs",
    "explanation": "買掛金は引き継がれるためストックです（ストックー＝BS）。"
    },
    {
    "question": "資本金は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "bs",
    "explanation": "資本金は引き継がれるためストックです（ストックー＝BS）。"
    },
    {
    "question": "水道光熱費は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "pl",
    "explanation": "水道光熱費はリセットされるためフローです（フロー＝PL）。"
    },
    {
    "question": "受取利息は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "pl",
    "explanation": "受取利息はリセットされるためフローです（フロー＝PL）。"
    },
    {
    "question": "建物は、BSとPLのどちらに表示される？",
    "choices": [
        ("bs", "BS"),
        ("pl", "PL")
    ],
    "answer": "bs",
    "explanation": "建物は引き継がれるためストックです（ストックー＝BS）。"
    }
]

bs_pl_reason_questions = [
    {
        "question": "なぜ収益や費用は損益計算書（PL）に表示されるのか？",
        "choices": [
            ("wrong1", "次の期間に引き継がれるから"),
            ("correct", "期末にリセットされるから"),
            ("wrong2", "現金に関係するから")
        ],
        "answer": "correct",
        "explanation": "収益や費用はフローであり、期間ごとにリセットされるため、損益計算書（PL）に表示されます。"
    },
    {
        "question": "なぜ資産は貸借対照表（BS）に残るのか？",
        "choices": [
            ("correct", "次の期間に引き継がれるから"),
            ("wrong1", "金額が大きいから"),
            ("wrong2", "期末にリセットされるから")
        ],
        "answer": "correct",
        "explanation": "資産はストックであり、期末の残高が次の期間に引き継がれるため、BSに表示されます。"
    },
    {
        "question": "なぜ費用は期末にゼロになるのか？",
        "choices": [
            ("wrong1", "次の期間に引き継がれるから"),
            ("correct", "期末にリセットされるから"),
            ("wrong2", "現金に変えるため")
        ],
        "answer": "correct",
        "explanation": "費用はフローであり、期間ごとにリセットされるため、期末にゼロになります。"
    },
    {
        "question": "なぜ収益と費用の結果を損益に集めるのか？",
        "choices": [
            ("correct", "期末にリセットされるから"),
            ("wrong1", "資産にするため"),
            ("wrong2", "次の期間に引き継がれるから")
        ],
        "answer": "correct",
        "explanation": "収益と費用をまとめることで、最終的な利益を計算するためです。"
    },
{
        "question": "なぜ資産はBSに残り、収益や費用はPLに行くのか？",
        "choices": [
            ("correct", "次の期間に引き継がれるから"),
            ("wrong1", "期末にリセットされるから"),
            ("wrong2", "現金に関係するから")
        ],
        "answer": "correct",
        "explanation": "ストックは次期に引き継がれ、フローは期間ごとにリセットされるためです。"
    }

]

bs_pl_reverse_questions = [
    {
        "question": "損益計算書（PL）に表示されるものはどれ？",
        "choices": [
            ("correct", "給料"),
            ("wrong1", "現金"),
            ("wrong2", "建物")
        ],
        "answer": "correct",
        "explanation": "給料は費用（フロー）なので、損益計算書（PL）に表示されます。"
    },
    {
        "question": "貸借対照表（BS）に表示されるものはどれ？",
        "choices": [
            ("correct", "現金"),
            ("wrong1", "給料"),
            ("wrong2", "水道光熱費")
        ],
        "answer": "correct",
        "explanation": "現金は資産（ストック）なので、貸借対照表（BS）に残ります。"
    },
    {
        "question": "次のうち、期末にゼロになるものはどれ？",
        "choices": [
            ("correct", "売上"),
            ("wrong1", "現金"),
            ("wrong2", "建物")
        ],
        "answer": "correct",
        "explanation": "売上は収益（フロー）なので、期末にリセットされゼロになります。"
    },
    {
        "question": "次のうち、次の期間に引き継がれるものはどれ？",
        "choices": [
            ("correct", "建物"),
            ("wrong1", "給料"),
            ("wrong2", "売上")
        ],
        "answer": "correct",
        "explanation": "建物は資産（ストック）なので、期末の残高が次の期間に引き継がれます。"
    }
]

worksheet_intro_questions = [
    {
        "question": "精算表は何のために作る？",
        "choices": [
            ("wrong1", "計算を楽にするため"),
            ("correct", "ストックとフローを分けるため"),
            ("wrong2", "試算表を作るため")
        ],
        "answer": "correct",
        "explanation": "精算表は、資産（ストック）と収益・費用（フロー）を分けるための表です。"
    },
    {
        "question": "なぜ分ける必要があるのか？",
        "choices": [
            ("correct", "BSとPLに分けるため"),
            ("wrong1", "金額を確認するため"),
            ("wrong2", "仕訳を書くため")
        ],
        "answer": "correct",
        "explanation": "最終的にBSとPLを作るために、ストックとフローを分ける必要があります。"
    },
    {
        "question": "精算表で分けられるものの組み合わせとして正しいのはどれ？",
        "choices": [
            ("correct", "資産と収益・費用"),
            ("wrong1", "現金と売上"),
            ("wrong2", "借方と貸方")
        ],
        "answer": "correct",
        "explanation": "資産はストック、収益・費用はフローなので、この2つを分けます。"
    }
]

worksheet_sort_questions = [
    {
        "account": "現金",
        "answer": "bs",
        "explanation": "現金は資産（ストック）なので、精算表では貸借対照表（BS）に入ります。"
    },
    {
        "account": "売上",
        "answer": "pl",
        "explanation": "売上は収益（フロー）なので、精算表では損益計算書（PL）に入ります。"
    },
    {
        "account": "給料",
        "answer": "pl",
        "explanation": "給料は費用（フロー）なので、精算表では損益計算書（PL）に入ります。"
    },
    {
        "account": "建物",
        "answer": "bs",
        "explanation": "建物は資産（ストック）なので、精算表では貸借対照表（BS）に入ります。"
    }
]

def grade_worksheet_amount(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        account = form.get(f"text{i}", "")
        side = form.get(f"side{i}", "")
        user_amount = normalize_amount(form.get(f"q{i}"))
        correct_amount = normalize_amount(form.get(f"a{i}"))
        explanation = form.get(f"e{i}", "")

        side_label_map = {
            "bs": "BS（貸借対照表）",
            "pl": "PL（損益計算書）"
        }

        side_label = side_label_map.get(side, side)
        is_correct = (user_amount == correct_amount)

        if is_correct:
            score += 1

        results.append({
            "account": account,
            "side": side_label,
            "user_amount": user_amount or "未入力",
            "correct_amount": correct_amount,
            "explanation": explanation,
            "is_correct": is_correct
        })

    return score, results

worksheet_amount_questions = [
    {
        "account": "現金",
        "side": "bs",
        "amount": "300000",
        "question": "試算表：現金 300000\nこの金額を精算表に移します。\n現金はいくら？",
        "explanation": "現金は資産（ストック）なので、精算表では貸借対照表（BS）に入ります。"
    },
    {
        "account": "売上",
        "side": "pl",
        "amount": "500000",
        "question":"試算表:売上 500000\nこの金額を精算表に移します。\n売上はいくら？",
        "explanation": "売上は収益（フロー）なので、精算表では損益計算書（PL）に入ります。"
    },
    {
        "account": "給料",
        "side": "pl",
        "amount": "120000",
        "question":"試算表:給料 120000\nこの金額を精算表に移します。\n給料はいくら？",
        "explanation": "給料は費用（フロー）なので、精算表では損益計算書（PL）に入ります。"
    },
    {
        "account": "建物",
        "side": "bs",
        "amount": "800000",
        "question":"試算表:建物 800000\nこの金額を精算表に移します。\n現金はいくら？",
        "explanation": "建物は資産（ストック）なので、精算表では貸借対照表（BS）に入ります。"
    }
]

def grade_worksheet_sort(form, num_questions):
    score = 0
    results = []

    for i in range(num_questions):
        account = form.get(f"text{i}", "")
        user = form.get(f"q{i}", "")
        answer = form.get(f"a{i}", "")
        explanation = form.get(f"e{i}", "")

        label_map = {
            "bs": "BS（貸借対照表）",
            "pl": "PL（損益計算書）"
        }

        user_label = label_map.get(user, "未回答")
        answer_label = label_map.get(answer, answer)

        is_correct = (user == answer)
        if is_correct:
            score += 1

        results.append({
            "question": f"{account}は精算表のどちらに入る？",
            "user_answer": user_label,
            "correct_answer": answer_label,
            "explanation": explanation,
            "is_correct": is_correct
        })

    return score, results

adjustment_reason_questions = [
    {
        "question": "100個仕入れて90個売れた。なぜ決算整理が必要？",
        "choices": [
            ("wrong1", "売上を増やすため"),
            ("correct", "費用を減らすため"),
            ("wrong2", "現金を増やすため")
        ],
        "answer": "correct",
        "explanation": "仕入を費用にしすぎているため、正しく減らす必要があります。"
    },
    {
        "question": "まだ使っていない分があるのに費用にしている状態は？",
        "choices": [
            ("wrong1", "収益が少ない"),
            ("correct", "費用が多すぎる"),
            ("wrong2", "資産が多すぎる")
        ],
        "answer": "correct",
        "explanation": "本来は資産として残るべきものを費用にしているためです。"
    },
    {
        "question": "決算整理とは何を正す作業？",
        "choices": [
            ("wrong1", "現金の増減"),
            ("correct", "費用と資産のズレ"),
            ("wrong2", "仕訳の数")
        ],
        "answer": "correct",
        "explanation": "費用にしすぎた部分を資産に戻すなど、ズレを修正します。"
    }
]

adjustment_journal_questions = [
    {
        "question": "100個仕入れて90個売れた。決算整理の仕訳は？",
        "choices": [
            ("correct", "繰越商品 / 仕入"),
            ("wrong1", "仕入 / 繰越商品"),
            ("wrong2", "現金 / 仕入")
        ],
        "answer": "correct",
        "explanation": "費用にしすぎた仕入を減らし、資産（繰越商品）に戻します。"
    },
    {
        "question": "費用を減らして資産に戻すときの仕訳は？",
        "choices": [
            ("correct", "資産 / 費用"),
            ("wrong1", "費用 / 資産"),
            ("wrong2", "収益 / 費用")
        ],
        "answer": "correct",
        "explanation": "費用を減らし、資産を増やす仕訳になります。"
    },
    {
        "question": "仕入を減らすとき、どちらに記入する？",
        "choices": [
            ("correct", "貸方"),
            ("wrong1", "借方"),
            ("wrong2", "どちらでもよい")
        ],
        "answer": "correct",
        "explanation": "費用（仕入）は借方にあるため、減らすときは貸方に記入します。"
    }
]

worksheet_flow_questions = [
    {
        "question": "試算表：仕入 100,000\n決算整理で10,000戻した\n最終的にPLにいくらいく？",
        "choices": [
            ("wrong1", "100000"),
            ("correct", "90000"),
            ("wrong2", "110000")
        ],
        "answer": "correct",
        "explanation": "仕入は100,000ですが、10,000戻すため、最終的な費用は90,000になります。"
    },
    {
        "question": "試算表：現金 300,000\n決算整理なし\n最終的にBSにいくらいく？",
        "choices": [
            ("correct", "300000"),
            ("wrong1", "0"),
            ("wrong2", "変わる")
        ],
        "answer": "correct",
        "explanation": "現金は資産（ストック）なので、そのままBSに残ります。"
    },
    {
        "question": "試算表：売上 500,000\n決算整理なし\n最終的にPLにいくらいく？",
        "choices": [
            ("correct", "500000"),
            ("wrong1", "0"),
            ("wrong2", "変わる")
        ],
        "answer": "correct",
        "explanation": "売上は収益（フロー）なので、そのままPLに集計されます。"
    }
]

worksheet_to_fs_questions = [
    {
        "question": "仕入 100,000 → 決算整理で10,000戻した\n最終的にどこに行く？",
        "choices": [
            ("correct", "PL（損益計算書）"),
            ("wrong1", "BS（貸借対照表）"),
            ("wrong2", "どちらでもない")
        ],
        "answer": "correct",
        "explanation": "仕入は費用（フロー）なので、最終的に損益計算書（PL）に集まります。"
    },
    {
        "question": "現金 300,000 → 決算整理なし\n最終的にどこに行く？",
        "choices": [
            ("correct", "BS（貸借対照表）"),
            ("wrong1", "PL（損益計算書）"),
            ("wrong2", "どちらでもない")
        ],
        "answer": "correct",
        "explanation": "現金は資産（ストック）なので、貸借対照表（BS）に残ります。"
    },
    {
        "question": "売上 500,000 → 決算整理なし\n最終的にどこに行く？",
        "choices": [
            ("correct", "PL（損益計算書）"),
            ("wrong1", "BS（貸借対照表）"),
            ("wrong2", "どちらでもない")
        ],
        "answer": "correct",
        "explanation": "売上は収益（フロー）なので、損益計算書（PL）に集まります。"
    }
]

mini_closing_questions = [
    {
        "question": "100個仕入（100,000）、90個売上（売上180,000）、10個残る\n決算整理後のPL（利益）はいくら？",
        "choices": [
            ("wrong1", "180000"),
            ("correct", "90000"),
            ("wrong2", "100000")
        ],
        "answer": "correct",
        "explanation": "売上180,000 − 費用90,000 = 利益90,000です。"
    },
    {
        "question": "同じ条件で、BSに残る商品はいくら？",
        "choices": [
            ("correct", "10000"),
            ("wrong1", "90000"),
            ("wrong2", "0")
        ],
        "answer": "correct",
        "explanation": "10個分が残るため、10,000が資産としてBSに残ります。"
    }
]



