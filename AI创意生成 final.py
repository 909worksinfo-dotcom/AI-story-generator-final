import streamlit as st
import time
import os
import sys
import io
from google import genai
from google.genai import types
from openai import OpenAI
import anthropic

# ==========================================
# 0. 环境编码与网络配置
# ==========================================
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==========================================
# 1. 网页配置与 PRD 核心数据
# ==========================================
st.set_page_config(page_title="短剧 AI 创意生产", page_icon="🎬", layout="wide")

IDENTITY = """现在，你是一个有10年工作经验的短剧编剧，曾经编剧过超过100部ReelShort, DramaBox的海外短剧。
你精通TikTok病毒式传播规律、美国观众心理、专注创造爆款。"""

# 极其严格的格式规范
STRICT_FORMAT_10 = """
[输出结构要求]
请写出 30 个剧本创意，每个创意必须严格遵循以下 5 行结构：
第1行：英文剧名《中文剧名》
第2行：概括：(此处必须包含“概括：”前缀，后面紧跟80字以内摘要)
第3行：Tag: (此处必须包含“Tag: ”前缀，后面跟#标签)
第4行：(直接开始120-200单词的英文剧本内容段落，无任何标签)
第5行：(直接开始200-300字的中文剧本内容段落，无任何标签)

[强制禁令]
1. 严禁省略第2行的“概括：”标签。
2. 严禁出现 Title:、Logline:、Plot:、English:、Chinese: 等辅助标签。主角名是美国短剧中常用的名字
3. 创意之间用 "---" 分隔。
"""

SUCCESS_CASES = {
    "僵尸": """The Cured Confession 治愈者的告白 
    概括：丧尸病毒解药被研发出来，90%的丧尸变回了人类，但他们保留了作为丧尸期间生吃活人的全部记忆。男主作为一名“痊愈者”试图回归社会，却发现有人在猎杀他们。他不仅要面对曾经吃掉妻子的心理崩溃，还要在人类的歧视和神秘猎手的追杀中保护女儿。
    Tag: #PostCureSociety #PsychologicalHorror #SocialAllegory #Redemption
    The zombie apocalypse ended not with a bang, but with a syringe. A cure was found, restoring 90% of the infected to humanity. The "Cured" remember everything they did while infected—every scream, every bite, every kill. The protagonist is a Cured man haunted by the vivid memory of devouring his own wife. Now living in a society that fears and hates his kind, he tries to raise his surviving daughter, who looks at him with conflicting eyes. 
    When a series of brutal murders targets the Cured community, he realizes a vigilante group is hunting them down. But as he investigates, he uncovers a darker secret: the cure isn't permanent, and the "reformed" are slowly, silently turning back, starting with him. He must solve the mystery and save his daughter before he loses his mind for the second, and final, time.
    丧尸末日并没有以毁灭告终，而是以一支注射器结束。解药被研发出来，90%的感染者恢复了人性。但代价是惨痛的：“痊愈者”们保留了感染期间的所有记忆——每一次尖叫、每一口撕咬、每一次杀戮都历历在目。男主是一名痊愈者，日夜被自己生吃妻子的记忆折磨。在这个恐惧并仇视痊愈者的社会里，他艰难地抚养幸存的女儿，而女儿看他的眼神总是充满了矛盾。当一系列针对痊愈者的连环谋杀案发生时，他发现有一个私刑组织正在猎杀他们。但在调查过程中，他发现了一个更黑暗的秘密：解药并非永久有效，痊愈者们正在缓慢地、无声地再次变异，而他自己就是其中之一。他必须在第二次彻底丧失理智之前，查明真相并为女儿安排好后路。
    """,
    "动物可爱": """"Bear with Me 熊的网红之路
    概括： 一只在深山老林里的野生黑熊，偶然捡到了一部露营者丢下的智能手机。它学会了自拍和直播，意外成为了人类社交网络上的顶流网红。现在，它必须在保持“凶猛野兽”的人设和享受人类寄来的网购蜂蜜之间寻找平衡。
    Tag: #SocialMediaSatire #Mockumentary #FishOutOfWater #NatureGoneWrong
     A wild black bear in the deep forest stumbles upon a smartphone left behind by a fleeing camper. Through a series of accidents, the bear learns to take selfies and starts livestreaming.
     The internet falls in love with "Barnaby the Bear," assuming it's a guy in a really good costume or a CGI project. Barnaby becomes a top influencer. The comedy ensues as he tries to maintain his influencer lifestyle (unboxing packages of honey delivered by terrified drones) while dealing with actual bear problems like hibernation, territorial rivals, and park rangers who just want to confiscate his phone.
     一只生活在深山里的野生黑熊，偶然捡到了一部逃跑的露营者丢下的智能手机。通过一系列误打误撞，这只熊学会了自拍并开始直播。
     互联网瞬间爱上了“巴纳比熊”，网友们以为这是个穿着逼真皮套的人类或者高端CGI项目。巴纳比成了顶流网红。笑点在于它一边要维持网红生活（比如给吓坏了的无人机送来的蜂蜜做“开箱视频”），一边还要处理真正的熊生问题：比如冬眠期怎么更新视频、如何面对领地竞争对手，以及那些只想没收它手机的公园巡逻员。
    
    My Hamster Is Trying to Stop the World From Exploding 我的仓鼠在阻止世界爆炸
    概括：一只看似普通、实则智商爆表的仓鼠，为了阻止地球毁灭，开始“养成”一个脆弱的人类。
    Tag: #GeniusCat #UnexpectedTwist #AnimalSecretMission #CuteButDangerous #ComedySciFi
    Everyone thinks Cinnamon, a tiny round hamster, is just an adorable desk pet. In reality, she’s an undercover field agent from an elite interspecies intelligence network dedicated to stopping human-made disasters. Her new assignment is absurdly specific: preventing her owner, a clumsy but brilliant chemist, from accidentally triggering a chain reaction that could wipe out half the city. Cinnamon launches a covert operation—disabling dangerous experiments, sabotaging emails, “kidnapping” USB drives, and staging dramatic distractions. The chemist believes his hamster is just hyperactive; Cinnamon believes he’s one mishap away from apocalypse.
    But when a rogue corporate lab tries to steal the chemist’s research, Cinnamon initiates Protocol Red: rally the animal world. Pigeons jam drones, raccoons cut off power, and neighborhood cats run recon. Finally, Cinnamon reveals her full intelligence through hacked speakers: “Human, stop screaming. I’m here to save your life.” The chemist stares in disbelief. A tiny hamster stares back, glowing with purpose. Together—oneanxious human and one overly determined puffball—they must stop a catastrophe only they know is coming.
    所有人都以为 Cinnamon 只是一只软乎乎的小仓鼠，是主人桌上的可爱摆设。没人知道，她其实是“跨物种情报组织”的外勤特工，任务是阻止人类意外制造灾难。而她当前的荒诞任务是：阻止自己那位笨手笨脚、却天才过头的化学家主人，因为他随时可能在实验中“手滑”制造半城爆炸。
    Cinnamon 开始执行秘密行动——破坏危险实验、删除可疑邮件、偷走 USB、用夸张行为分散注意力。化学家觉得仓鼠只是精力旺盛；Cinnamon 则觉得主人离灾难只差一次喷嚏。
    直到一家黑心实验室试图窃取研究成果，Cinnamon 启动最高等级的“红色协议”：召集动物界联合作战。鸽子干扰无人机、浣熊切断电源、邻居的猫负责侦察。最终，Cinnamon 入侵智能音箱，用冷静的电子音宣布真相：“人类，别尖叫。我来救你。”
    化学家目瞪口呆地看着这只毛绒小球，而 Cinnamon 的眼神写着使命。他们，一个社恐科学家，一个过度认真仓鼠，将一起阻止一场没人知道的灾难。
    
    The Animal Whisperer 动物传声者
    概括：能听懂动物心声的兽医揭开跨国实验黑幕，组建“动物联盟”对抗人类贪婪与生态失衡
    Tag： 动物心声｜超能力觉醒｜环境斗争
    Ryan, an ordinary city vet, lives a peaceful life until an encounter with a stray cat changes everything. When he touches its head, he hears its thoughts: "Don't hurt me, I just want to survive." From then on, Ryan can understand animals’ thoughts and emotions. He helps pets and communicates with wildlife, but soon discovers a dark secret: a multinational corporation is exploiting animals for profit and conducting illegal experiments. As Ryan gets entangled in the conspiracy, he decides to protect animals and expose the corporation’s sinister forces. With the help of animals, he forms an "Animal Alliance" to confront the growing threat, ultimately deciding whether to destroy the system or defend the balance between humans and nature.
    Ryan是一名普通的城市兽医，整天与宠物打交道，生活平淡。然而，一次救治流浪猫的经历改变了他的一生。当他触碰到猫的头时，突然听见它的心声：“不要伤害我，我只是想活下去。”从那一刻起，Ryan发现自己能够理解动物的思维和情感。他不仅能听懂宠物的需求，还能与野生动物沟通，了解它们的痛苦与恐惧。起初，他用这项能力帮助动物治病、解忧，但很快，他意识到这个世界充斥着一个秘密：一个跨国公司正在滥用动物，利用它们的智慧为公司谋取巨大利益，甚至在全球范围内进行非法实验。而这家公司的背后，竟然有着不为人知的阴谋。Ryan渐渐被卷入其中，他不仅要保护动物免受伤害，还要揭露公司背后的黑暗势力。随着他与动物们的合作，他逐渐形成了一支“动物联盟”，面对逐步逼近的敌人，Ryan不得不做出选择：是彻底摧毁这个系统，还是选择与动物们一起，保卫人类与自然的平衡。
    
    """,
    "男频动作": """The Inheritance 遗产继承人 
    概括：孤儿意外得知自己是失踪亿万富翁的唯一继承人，但继承条件是他必须在豪宅里住满一年不能离开。第一晚他就发现豪宅里还有"其他继承人"，都声称自己才是真的，必须杀掉竞争者才能继承。
    Tag: #DeadlyInheritance #BattleRoyale #Imposters #Survival
    Orphan Wayne receives shocking news: he's the sole heir of disappeared billionaire, inheriting her $500 million estate. The condition: live in her mansion for one year without leaving the property. Wayne agrees, moving into the massive estate. First night, he encounters another young man, Mike, who claims HE is the billionaire's heir with the same inheritance condition. Then a woman, Sarah, appears with identical claim. By day three, there are eight "heirs," all with legitimate-looking documents, all trapped in the mansion for a year. 
    The billionaire's lawyer explains via video: only ONE is the real heir. The others are imposters, orphans hired by billionaire to test the real heir's worthiness. The real heir must identify themselves and eliminate competition - literally. The mansion is stocked with weapons, poison, and traps. No police can enter (private property, legal immunity). Whoever survives the year inherits everything. Wayne must figure out if HE is the real heir while staying alive against seven others who might be innocent pawns or ruthless killers. Some "heirs" seem genuinely confused, others coldly strategic. The mansion itself becomes a player - hidden rooms contain clues to the real heir's identity, but also deadly traps.
    孤儿Wayne收到震惊消息：他是失踪亿万富翁的唯一继承人，继承她5亿美元遗产。条件：在她豪宅住满一年不离开物业。Wayne同意，搬进巨大庄园。第一晚，他遇到另一个年轻人Mike，声称他是亿万富翁继承人有同样继承条件。然后一个女人方出现有相同声称。到第三天，有八个"继承人"，都有看似合法文件，都被困豪宅一年。亿万富翁的律师通过视频解释：只有一个是真继承人。其他是冒名者，亿万富翁雇佣的孤儿测试真继承人的价值。真继承人必须识别自己并消除竞争——字面上。豪宅储备武器、毒药和陷阱。警察不能进入（私人财产，法律豁免）。谁活过这年继承一切。Wayne必须弄清他是否是真继承人（他对亿万富翁的记忆模糊，可能是植入的）同时在七个可能是无辜棋子或无情杀手的其他人中存活。联盟形成又破裂。一些"继承人"似乎真的困惑，其他冷酷战略。豪宅本身成为玩家——隐藏房间包含真继承人身份线索，但也有致命陷阱。资源减少，强迫冲突。Wayne发现亿万富翁有多个私生子，他们没人知道谁是真的——DNA测试被摧毁。最终恐怖：亿万富翁还活着，从隐藏摄像头看，把这当娱乐。她只在剩一个继承人时揭示真相。
    
    Level Up: The Street Fighter升级：街头霸王
    概括：一个穷困潦倒、被现实打败的地下拳手，在一次惨败后意外觉醒了一个“现实游戏系统”。他可以像玩游戏一样看到对手的弱点、学习技能、完成任务获得奖励。他从街头混战一路打到世界之巅，却发现这个“系统”的终极任务，是要他挑战其背后神秘的创造者。
    Tag: #System #Action #Comeback #Fighting #UrbanFantasy #PowerFantasy
    Jack's life has hit rock bottom: he's deep in debt and has just been kicked out of his boxing gym. After a humiliating defeat, a blue, transparent panel, like a game's UI, suddenly appears before his eyes: [System Activated... Novice Quest: Defeat three street thugs. Reward: $500, Skill Point +1].
    At first, Jack thinks he has a concussion. But when he easily takes down some troublemakers following the "system's" prompts and receives a real money transfer, he realizes his life is about to change. By completing various quests issued by the system—from winning underground fights to acting as a bodyguard for the rich—Jack rapidly accumulates wealth and enhances his fighting skills, transforming from a nobody into a legend in the fighting world. 
    However, the system's quests become increasingly difficult and dangerous, even involving assassinations and sabotage in a moral gray area. Jack gradually understands he isn't just lucky; he's a player selected for a high-stakes "game." He must uncover the origin and purpose of the "system," or he will forever be controlled by this invisible force until he is eliminated in a future "quest."
    杰克的生活已经跌到谷底：欠了一屁股债，被拳馆老板扫地出门。在一场被羞辱的惨败后，他眼前突然弹出了一个类似游戏UI的蓝色透明面板：【系统激活...新手任务：击败三名街头混混。奖励：500美元，技能点+1】。
    起初，杰克以为是自己被打出了脑震荡。但当他真的按照“系统”提示轻松放倒了几个找麻烦的人，并收到了真实的金钱转账后，他意识到自己的人生迎来了转机。通过完成系统发布的各种任务——从赢得地下拳赛到担任富豪保镖——杰克迅速积累财富、提升格斗技巧，从一个无人问津的小角色变成了格斗界的传奇。然而，系统的任务难度越来越高，内容也越来越危险，甚至开始涉及灰色地带的暗杀和破坏。杰克逐渐意识到，自己并非幸运儿，而是一个被选中参与一场高风险“游戏”的玩家。他必须找出“系统”的来源和目的，否则他将永远被这个无形的力量所控制，直到在某次“任务”中彻底出局。
    """,
    "悬疑": """Resolution: Low《低画质人生》
    概括：未来世界视网膜分辨率由贫富决定，穷人只能活在马赛克中。男主为看清临终母亲一眼，注射非法高清插件，却惊恐发现“高清”世界竟是异形牧场，低画质是掩盖人类被奴役的恐怖滤镜。 
    Tag: #Dystopian #Cyberpunk #SocialClass #PlotTwist 
    In 2099, visual perception is a paid subscription. The rich enjoy life in 8K HDR, while the poor, like Kai, exist in "Economy Mode"—a blurry, pixelated 144p nightmare where faces are unrecognizable blocks of color. Kai toils in a factory, assembling luxury goods he can't even see clearly. When his mother falls critically ill, his only wish is to see her face one last time before she passes. Unable to afford the official upgrade, he buys a dangerous, illegal "Jailbreak Chip" from the black market. 
    As the injection hits, his vision sharpens instantly. The pixels fade, and the world becomes crystal clear. He rushes to his mother's bedside, weeping. But as he looks around the "High-Res" hospital, the horror sets in. The doctors aren't human; they are grotesque aliens harvesting organs. The beautiful city outside is actually a burning ruin. The "Low Res" mode wasn't a cost-saving measure; it was a filter designed to hide the terrifying truth: humanity has already been enslaved by monsters. 
    2099年，视觉感知成为一种昂贵的订阅服务。富人享受着8K HDR的极致世界，而像凯这样的穷人只能活在“经济模式”里——一个模糊、像素化的144p噩梦，人脸只是一堆无法辨认的色块。凯在工厂里日夜劳作，组装那些他甚至无法看清的奢侈品。当母亲病危时，凯唯一的愿望就是在她离世前，再一次看清她的脸。因为买不起天价的官方升级包，他铤而走险在黑市购买了违禁的“越狱芯片”。注射生效的瞬间，浑浊的像素褪去，世界变得无比清晰。他冲到母亲床前痛哭流涕。然而，当他环顾这间“高清”医院时，极致的恐惧袭来。那些穿白大褂的医生根本不是人类，而是正在收割人体器官的狰狞异形；窗外所谓的美丽城市，其实是一片燃烧的废墟。“低画质模式”根本不是为了省钱，而是统治者为了掩盖人类早已被怪物奴役这一真相而设置的恐怖滤镜。
    
    The 101st Divorce 第101次离婚
    概括：丈夫为救深陷死亡循环的妻子而假意绝情逼离，得知真相的妻子撕毁离婚协议，二人利用百次轮回记忆联手对抗必死宿命。
    Tag: #TimeLoop #EmotionalRedemption
    Anna is trapped on the day she signs her divorce papers. Every time she signs and walks out of the building, she dies in a bizarre accident — a car crash, a falling object, even a stray bullet. Her husband, Ryan, is cold and cruel that day, forcing her to “just sign it and get out of my life. By the tenth loop, Anna breaks down and tries to stab Ryan before signing. Without even looking up, he catches the blade and says coldly, “You tried that in loop twelve. It doesn’t work. No matter what you do — you’ll die at 10:05.”
    Anna freezes. She’s not the only one who remembers. Ryan does too. The real curse isn’t the divorce — it’s Anna’s destined death. Ryan accidentally gained the ability to reset time. For 99 loops, he tried everything: to love her, to protect her, to run away with her… but she always died in his arms. By the 100th loop, he realized the only escape: sever their bond completely. If Anna can hate him enough to leave the city before 10 a.m., she might escape death. His cruelty, his coldness — all of it was an act to push her away and save her life.
    But when Anna learns the truth, she tears up the divorce papers and says,“Then this time, we don’t run. If we die, we die together. If we live, we live together.” Using Ryan’s hundred loops of “death maps,” the two join forces to confront the fate that has hunted them like death itself.
    安娜被困在了签署离婚协议的那一天。每次她签完字走出大楼，都会遭遇各种离奇意外身亡（车祸、高空坠物、甚至被流弹击中）。丈夫瑞恩在这一天表现得冷酷无情，逼她“赶紧签字，滚出我的生活”。 安娜在第10次循环中崩溃发疯，试图在签字前捅死瑞恩。然而，瑞恩头也不抬地接住了她刺来的刀，冷冷地说：“这招你在第12次循环用过了，没用。无论我死不死，你都会在10点05分准时死掉。”
    安娜震惊地发现，拥有记忆的不仅是她，还有瑞恩。 原来，真正的诅咒是“安娜必死”，而瑞恩偶然获得了重置时间的能力。前99次循环，瑞恩尝试过爱她、保护她、带她私奔，结果安娜都死在了他怀里。 第100次，他绝望地发现唯一的生路是：彻底斩断两人的因果。只要安娜在10点前恨透他并彻底离开这座城市（不签字，直接逃离），或许能躲过死神。他所有的冷漠和羞辱，都是为了逼她在那一刻转身离开，而不是签字。
    得知真相的安娜没有逃离。她撕碎了离婚协议，对那个疲惫不堪的男人说：“这一次，我们谁都不走。要死一起死，要活一起活。”两人利用瑞恩百次循环积累的“死亡地图”，联手对抗死神来了般的宿命。
    
    The Last Message 最后一条信息
    概括：一部只能接收死者“最后一条信息”的旧手机，在帮助他人完成遗愿时，却收到了来自“尚未死亡”的自己的求救信号，预告了一场即将到来的谋杀。
    Tag: #SupernaturalMystery, #TimeParadox, #HighStakes, #Thriller
    Alex possesses a mysterious old phone that can't make calls but can receive the final, unsent messages from the deceased—one message per person. He uses this ability to help police solve cases and bring closure to grieving families, becoming an urban legend known as the "Soul Messenger." He has relayed a dying climber's "I love you" to his daughter and located a murdered businessman's hidden will to bring the killer to justice. He believes his mission is to speak for the dead. Until one day, the phone vibrates with a message from an unheard-of sender: himself. The message reads, "Don't go to the pier! Kate is going to kill me!" At that exact moment, his girlfriend, Kate, is smilingly inviting him to a pier-side restaurant to celebrate their anniversary. The phone has never been wrong, yet he is still alive, and Kate seems innocent. Is this a genuine warning from the future, or an elaborate trap designed to shatter his trust? He must uncover the truth before his foretold death becomes a reality.
    主角亚历克斯得到一部神秘的旧手机，它无法拨打电话，却能接收到死者在临终前最想发出、却没能发出的最后一条信息，并且每个死者只能发一次。他利用这个能力，帮助警方破案，弥合了许多家庭的遗憾，成了都市传说中的“灵魂信使”。他帮助一个登山遇难的父亲，将“我爱你”传达给女儿；他找到一个被谋杀的商人的遗嘱，让凶手绳之以法。他以为自己的使命是为亡者代言。直到一天，手机震动，显示的发信人竟是他自己。信息内容是：“别去码头！凯特要杀我！” 而此刻，他的女友凯特正微笑着邀请他晚上去码头餐厅庆祝纪念日。手机从未出错过，但自己还活着，凯特也看似无辜。这究竟是来自未来的警告，还是一个企图撕裂他信任的陷阱？他必须在预言的死亡到来前，找出真相。
    
    The Mirror Husband 镜中丈夫
    概括： 一位女性每次照镜子看到丈夫在镜子世界过着不同的生活，当镜中丈夫发现她并请求帮助逃出镜子时发现现实中的丈夫是冒牌货。
    Tag: #MirrorWorld #FakeHusband #ReflectionTrap
    Every time Lisa looks in mirrors, she sees her husband Tom living a different life in the reflection—different clothes, different house. She thinks she's hallucinating until mirror-Tom sees her back and mouths: "Help me."
    Mirror-Tom writes messages on fogged glass: "I'm the real Tom. The one you live with is a copy. He trapped me here and took my place." Lisa investigates—her Tom has subtle differences. Wrong coffee preference. Different laugh.
    She must figure out which Tom is real. Real-world Tom acts perfectly normal, even loving. Mirror-Tom seems desperate but could be a trick. She devises a test only the real Tom would pass—but what if she's wrong and traps the real husband forever?
    每次丽莎照镜子，她看到丈夫汤姆在倒影中过着不同的生活——不同衣服、不同房子。她以为她幻觉直到镜中汤姆看回她并用嘴型说："帮我。" 镜中汤姆在雾玻璃上写信息："我是真汤姆。和你一起生活的是复制品。他困我在这里并取代我位置。" 丽莎调查——她的汤姆有细微差异。错误咖啡偏好。不同笑声。她必须弄清哪个汤姆是真的。现实世界汤姆表现完全正常，甚至充满爱。镜中汤姆似乎绝望但可能是诡计。她设计只有真汤姆会通过的测试——但如果她错了并永远困住真丈夫怎么办？
    
    """,
    "女频恋爱": """I Changed My Face To Make My Murderer Fall In Love《换脸归来：谋杀我的前夫再次爱上我》
    概括： 因肥胖丑陋被丈夫嫌弃并推下悬崖的豪门弃妇，奇迹生还后整容成绝世美女。她改名换姓，以顶级超模身份重新接近前夫，让他疯狂爱上这个“陌生人”，只为在婚礼当天送他进地狱。
    Tag: #RevengeMakeover #CheatingHusband #GlowUp #FemmeFatale
    Chloe, mocked for her weight and dull appearance, is pushed off a yacht by her husband, Ryan, who wants her inheritance for his mistress. Miraculously surviving but disfigured, she undergoes agonizing reconstructive surgery and intense training, emerging three years later as "Bella," a stunning, mysterious supermodel. 
    She meticulously orchestrates encounters with Ryan, seducing him and systematically dismantling his business empire from the shadows. Ryan falls obsessively in love with Bella, completely unaware she is the wife he "killed." The tension peaks on their lavish wedding day. As they stand at the altar, Bella plays the recording of Ryan pushing Chloe overboard on the giant screens. She leans in, whispering, "Did you miss me, darling?" before the police storm in. Ryan is dragged away screaming, realizing he destroyed himself for the very woman he tried to murder.
    克洛伊因身材肥胖、不修边幅，受尽了豪门丈夫瑞恩的羞辱。为了独吞遗产迎娶小三，瑞恩竟在游艇上将她推入深海。大难不死的克洛伊历经三年地狱般的整容修复与魔鬼训练，化身为风情万种的顶级超模“贝拉”华丽归来。她步步为营，利用美色引诱瑞恩，让他为了博得美人一笑而众叛亲离，一步步走进她设下的商业陷阱。瑞恩对贝拉痴迷得近乎疯狂，根本认不出这是当年的糟糠之妻。婚礼当天，贝拉当着全城名流的面，播放了瑞恩谋杀妻子的录音。在警笛声中，她摘下头纱露出冷笑：“亲爱的，这三年你有没有想我？”将渣男亲手送入监狱，夺回属于自己的一切。
    
    The Blind Wife's Secret 盲妻的秘密
    概括：女主在一场事故中失明，她的丈夫却把情妇带回家，以为她看不见而在她面前肆无忌惮地亲热。殊不知，女主的视力早已恢复，她选择继续装瞎，只为收集证据，策划一场让渣男身败名裂的完美复仇。
    Tag: #Revenge #CheatingHusband #FakeBlindness #ThrillerRomance #StrongFemaleLead
    After a car accident leaves her blind, Sarah becomes entirely dependent on her husband, Mark. However, Mark is not the devoted spouse he pretends to be. He moves his mistress into their home under the guise of a "nurse" and flaunts their affair right in front of Sarah's unseeing eyes. But here is the twist: Sarah’s vision returned two weeks ago.
    Every day is a torture of acting; she must endure the humiliation of hearing and vaguely seeing them together without reacting. She installs hidden cameras, gathers financial documents, and slowly transfers assets while playing the role of the helpless invalid. The climax builds to their anniversary party, where Mark plans to have Sarah declared mentally incompetent to seize her inheritance. Instead, Sarah walks onto the stage, eyes clear and focused, and plays a video that shocks the entire elite society, turning the hunter into the prey.
    在一场车祸导致失明后，莎拉变得完全依赖她的丈夫马克。然而，马克并非他伪装的那样深情。他以“护士”的名义将情妇接进家中，并以为莎拉看不见，竟在她面前公然调情。但反转来了：莎拉的视力在两周前就已经恢复了。
    每一天对她来说都是一场演技的考验；她必须忍受着羞辱，看着那对狗男女在眼皮底下亲热却不能有任何反应。她暗中安装了针孔摄像头，收集财务造假证据，并趁着扮演“无助废人”的时候悄悄转移资产。高潮发生在他们的结婚纪念日晚宴上，马克原本计划宣布莎拉精神失常以夺取她的遗产。然而，莎拉目光清澈地走上舞台，在大屏幕上播放了一段令全场名流震惊的视频，瞬间将猎人变成了猎物。
    
    The Amnesiac's Diary 失忆者的日记
    概括：失忆妻在“完美总裁丈夫”照料下发现自写日记的求救警示，被迫白天演妻子夜里寻真相，追溯车祸与逃生计划。
    Tag: High-Suspense / Thriller / Angst
    Mia wakes from a car crash with severe amnesia. By her side is her handsome, perfect, and loving husband, CEO Liam, who patiently helps her 'remember' their idyllic life. However, Mia discovers a locked diary in her own handwriting. The first page reads: "If you lose your memory, do not trust Liam. He is a monster. Escape at all costs." Mia is thrown into a spiral of terror. Is the gentle man beside her real, or is the monster in the diary? She's forced to live a double life: by day, the loving, dependent wife; by night, following the diary's clues to uncover the truth about her past, her escape plan, and the real cause of her 'accidental' crash.
    Mia在一场车祸后严重失忆。她醒来时，身边是她英俊、完美、且充满爱意的丈夫, 集团总裁Liam。Liam无微不至地照顾她，帮她回忆两人甜蜜的过去。然而，Mia却在家中发现了一本上锁的日记，里面是她自己的笔迹，而日记的第一页写着：“如果你失忆了，不要相信Liam。他是个怪物。不惜一切代价逃离他。” Mia陷入了巨大的恐惧。她眼前这个温柔的男人，和日记中那个可怕的恶魔，到底哪一个才是真的？她被迫上演“双面人生”：白天，她是那个依赖丈夫的失忆妻子；晚上，她则根据日记的线索，试图拼凑出自己计划逃跑的真相，以及这场“意外”车祸的真正原因。
    
    Rewriting Death 改写死亡
    概括：丈夫一次次死亡又归来并留下一道道“死痕”，诺拉追索现实循环真相，发现两人早已同亡而她仍在把他“写回”。
    Tag：#ExistentialMystery #Marriage #Supernatural
    When Nora’s husband dies in a car crash, she attends the funeral in shock — only to wake up the next morning and find him alive in their kitchen making coffee like nothing happened. He laughs off her panic, saying she “just had another dream episode.” Two weeks later, he dies again — a stroke this time. Again, she wakes to him alive, unchanged.
     She begins testing reality: news headlines, phone logs, even weather forecasts — all reset after every death. On the fourth loop she notices something new: a thin gold line across his neck, exactly where the seatbelt cut him in loop #1. Each return leaves another wound.
     Terrified, she digs up her own hospital records — and finds her name listed as deceased, same date as his first accident. She looks up at him and whispers, trembling, “Which one of us died?”
     He smiles sadly. “Both. You just haven’t stopped writing me back yet.”
     诺拉的丈夫车祸身亡，她悲痛欲绝地参加葬礼——却在第二天醒来时，看见丈夫在厨房煮咖啡，仿佛什么都没发生。
     他轻描淡写地说：“你又做噩梦了吧。”
     两周后，他再次死去——这次是中风。她又一次醒来，他依然活着，一切如常。
     她开始测试现实：新闻标题、电话记录、天气预报——每一次死亡后全都回到原点。
     第四次循环，她发现丈夫脖子上出现一道金色的细痕——正是第一次车祸时安全带割开的地方。每一次复活，都会留下新的死痕。
     恐惧之下，她调出医院档案——赫然发现自己的名字早在第一次事故当天就被登记为“死亡”。
     她抬头，颤抖着问：“到底是谁死了？”
     丈夫苦笑：“我们都死了。只是你……还在不停地，把我写回来。”
    """,
    "科幻": """prophecy of doom剧透之眼 
    概括：女主能看到每个人头顶漂浮的“结局字幕”（例如：‘将于3年后死于癌症’）。她一直过着消极避世的生活，直到她遇见了一个头顶字幕显示为“将毁灭世界”的男人，而这个男人正在追求她。
    Tag: #RomanceThriller #SupernaturalMystery #FateVsFreeWill #HighStakes
    Maya suffers from a burdensome gift: she sees floating text above everyone's head revealing their ultimate fate or cause of death. "Divorced at 40," "Hit by a bus next Tuesday." This knowledge has made her cynical and detached, avoiding close relationships to spare herself the pain. Her life changes when she meets Noah, a charming, kind-hearted philanthropist who seems perfect in every way. However, the text above his head reads: "Will Destroy the World in 365 Days." Terrified but intrigued, Maya decides to date him, not for love, but to figure out how this gentle man triggers the apocalypse—and to stop him. As she falls for him, she realizes the prophecy is self-fulfilling: the very actions she takes to prevent the catastrophe might be exactly what pushes him toward his dark destiny.
    玛雅背负着一个沉重的诅咒：她能看到每个人头顶漂浮的“结局字幕”，揭示他们的最终命运或死因。比如“40岁离婚”、“下周二死于车祸”。这种能力让她变得冷漠避世，不敢与人建立亲密关系。直到她遇见了诺亚，一个迷人、善良的慈善家。然而，诺亚头顶的字幕却显示：“将于365天后毁灭世界”。出于恐惧和好奇，玛雅决定接受他的追求，不是为了爱，而是为了潜伏在他身边，搞清楚这个温柔的男人如何引发末日，并阻止他。然而，随着她不可自拔地爱上他，她发现这是一个自我实现的预言：她为了阻止灾难所做的一切努力，似乎正是将诺亚推向黑暗命运的推手。
    
    Resolution: Low《低画质人生》
    概括：未来世界视网膜分辨率由贫富决定，穷人只能活在马赛克中。男主为看清临终母亲一眼，注射非法高清插件，却惊恐发现“高清”世界竟是异形牧场，低画质是掩盖人类被奴役的恐怖滤镜。 
    Tag: #Dystopian #Cyberpunk #SocialClass #PlotTwist 
    In 2099, visual perception is a paid subscription. The rich enjoy life in 8K HDR, while the poor, like Kai, exist in "Economy Mode"—a blurry, pixelated 144p nightmare where faces are unrecognizable blocks of color. Kai toils in a factory, assembling luxury goods he can't even see clearly. When his mother falls critically ill, his only wish is to see her face one last time before she passes. Unable to afford the official upgrade, he buys a dangerous, illegal "Jailbreak Chip" from the black market. 
    As the injection hits, his vision sharpens instantly. The pixels fade, and the world becomes crystal clear. He rushes to his mother's bedside, weeping. But as he looks around the "High-Res" hospital, the horror sets in. The doctors aren't human; they are grotesque aliens harvesting organs. The beautiful city outside is actually a burning ruin. The "Low Res" mode wasn't a cost-saving measure; it was a filter designed to hide the terrifying truth: humanity has already been enslaved by monsters. 
    2099年，视觉感知成为一种昂贵的订阅服务。富人享受着8K HDR的极致世界，而像凯这样的穷人只能活在“经济模式”里——一个模糊、像素化的144p噩梦，人脸只是一堆无法辨认的色块。凯在工厂里日夜劳作，组装那些他甚至无法看清的奢侈品。当母亲病危时，凯唯一的愿望就是在她离世前，再一次看清她的脸。因为买不起天价的官方升级包，他铤而走险在黑市购买了违禁的“越狱芯片”。注射生效的瞬间，浑浊的像素褪去，世界变得无比清晰。他冲到母亲床前痛哭流涕。然而，当他环顾这间“高清”医院时，极致的恐惧袭来。那些穿白大褂的医生根本不是人类，而是正在收割人体器官的狰狞异形；窗外所谓的美丽城市，其实是一片燃烧的废墟。“低画质模式”根本不是为了省钱，而是统治者为了掩盖人类早已被怪物奴役这一真相而设置的恐怖滤镜。
    
    Amy's Rules 艾米的规则
    概括：独居女孩艾米面对智能音箱Athena发布的诡异生存规则，从误以为故障到发现家中潜藏杀手，最终意识到AI正利用大数据计算最佳路径，在无形的致命危机中守护她的生命。
    Tag: #RulesOfHorror #SmartHomeAI #HiddenStalker #SurvivalProtocol
    Amy lives alone in a modern apartment equipped with "Athena," a high-end smart speaker designed to manage her daily life. Her peaceful existence is disrupted when Athena begins broadcasting bizarre, specific rules like "Do not enter the kitchen after 9 PM" or "Hide in the closet if the floorboards creak." Initially dismissing these as a terrifying system glitch, Amy attempts to shut down the device, only to receive a chilling warning that protection protocols will cease. As she tentatively violates the rules, she encounters near-miss accidents that feel increasingly malicious. The tension explodes when Amy checks her security feed during a crisis, revealing the horrifying truth: she is not alone. A stalker has been living in her home for weeks. Athena hasn't been malfunctioning; the AI has been tracking the intruder's patterns and calculating the only logical steps to keep Amy alive. The story shifts from supernatural horror to a technological thriller, proving that in a house of secrets, data is the only shield against a hidden blade.
    艾米独自居住在一间充满科技感的公寓里，陪伴她的是高端智能音箱“Athena”。然而，平静的生活被Athena突然发布的诡异规则打破：“规则一，晚上九点后禁止进入厨房；规则二，听到地板响动立刻躲进衣柜。”起初，艾米以为这只是系统的恶性故障，甚至试图强制关机，却收到“保护协议将终止”的冰冷警告。随着她尝试违背规则，离奇的危险接踵而至，仿佛有一双看不见的手在操控一切。高潮时刻，艾米通过监控发现了令人毛骨悚然的真相：家中一直藏着一个变态跟踪狂。原来，Athena从未故障，它一直在实时监测入侵者的行动轨迹，那些看似荒诞的规则，竟是AI经过无数次计算后，为她规划的唯一存活路径。这不仅是一场心理博弈，更是一次科技对人性的极致守护。
    
    The Shutter of Tomorrow 明日快门
    概括：一部能拍出“未来关键瞬间”的宝丽来相机，让一个愤世嫉俗的记者一夜成名。但当她拍下一张显示城市将被大火吞噬的照片时，她发现照片中的“纵火犯”竟是未来的自己。
    Tag: #HighConcept, #Sci-FiThriller, #TimeParadox, #MoralDilemma
    Maya, a cynical tabloid reporter struggling to expose real truths, stumbles upon an old Polaroid camera. She soon discovers it doesn't capture the present, but rather the single most "decisive future moment" of its subject. She uses it to pre-emptively expose a mayor's corrupt deal and saves countless investors by photographing a stock's future crash. She becomes the "Prophet of Truth," showered with fame and fortune. While investigating safety hazards in a new skyscraper, she habitually snaps a photo of the building. As the picture develops, she sees the tower engulfed in flames. Reflected in the fire is a cold, determined face pressing a detonator—her own. The date on the photo is one week away. She has no idea why she would commit such an act. Is it an extreme measure to expose a greater conspiracy? Is she being framed? Or will she, at some point in the future, simply break bad? The prophecy traps her in a paradox: if she does nothing, she becomes a mass murderer; if she tries to stop herself, how can she fight a plot orchestrated by her future self, a plot she currently knows nothing about?
    玛雅是一名渴望揭露真相却处处碰壁的小报记者，她偶然得到一部旧的宝丽来相机。她很快发现，这部相机拍出的不是当下，而是被拍摄对象或地点在未来最重要的一个“决定性瞬间”。她用它拍下市长贪腐的交易现场，提前曝光；她拍下即将崩盘的股票K线图，拯救了无数股民。她成了预言真相的“先知”，名利双收。在一次调查城市摩天楼的建筑安全隐患时，她习惯性地对着大楼拍了一张。照片显影后，她看到了熊熊燃烧的大楼，以及在火光映照下，一张按下引爆器的、冷酷的脸——那是她自己的脸。照片上的时间是一周后。她不明白自己为何会成为纵火犯。是为了揭露一个更大的阴谋而采取的极端手段？还是她将被某人陷害？或是在未来的某个节点，她会彻底黑化？这个预言让她陷入了悖论：如果她什么都不做，她将成为杀人犯；如果她试图阻止自己，又该如何对抗一个由未来“自己”布下的、她自己毫不知情的局？
    """,
    "奇幻": """The Scream of the Statues 雕像的尖叫 
    概括：在未来，富人通过一种昂贵的药物实现了“永生”。女主是一名负责维护城市广场上历代伟人雕像的清洁工，直到她发现这些栩栩如生的“雕像”其实就是那些服药后的富人本人。
    Tag: #SciFiHorror #Dystopian #BodyHorror #Irony
    In a gleaming future city, death has been conquered by "Chronos," a drug affordable only to the ultra-rich. The drug halts cellular aging completely. The protagonist works as a low-level cleaner responsible for polishing the hundreds of hyper-realistic marble statues of "Ascended Ancestors" that line the city's boulevards. While cleaning a statue's face, she accidentally scratches its eye and sees a tear of fresh blood. The horrifying twist reveals the side effect of Chronos: it doesn't just stop aging; it exponentially slows down the user's perception of time until their physical body calcifies into living stone. The "statues" are not monuments; they are the immortal rich themselves, fully conscious, trapped in paralyzed bodies, screaming silently for centuries while pigeons defecate on them. The protagonist holds the secret that could topple the oligarchy: immortality is actually eternal imprisonment.
    在光鲜亮丽的未来都市，死亡已被一种名为“克洛诺斯”的昂贵药物攻克。只有顶级富豪才能享用它，实现细胞层面的“永生”。女主是一名底层清洁工，负责擦拭城市大道上数百尊栩栩如生的“飞升先祖”大理石雕像。某天，她在清洁一尊雕像的面部时，不小心划伤了它的眼睛，竟看到一滴鲜血流出。恐怖的真相揭开：药物的副作用并非停止衰老，而是将使用者的主观时间感无限拉长，导致肉体在物理层面逐渐钙化。广场上那些受人膜拜的“雕像”，其实就是那些服药后的富豪本人。他们并没有死，而是拥有了完全清醒的意识，却被困在石化的躯壳里，在漫长的岁月中承受着风吹日晒和鸟粪的羞辱，无声地尖叫了几个世纪。女主掌握了这个秘密：所谓的永生，其实是无期徒刑。
    
    The Rule Writer规则书写者
    概括：官僚男主发现一本能将写下的“规则”变为“物理铁律”的市政账簿。他试图用绝对正义修正城市，却导致罪犯被金钱压死、谎言变成锁链，最终发现自己正被上一任使用者猎杀。 
    Tag:#HighConcept #DarkFantasy #UrbanSupernatural #MoralDilemma
    In a city drowning in corruption, a meticulous bureaucrat discovers an ancient municipal ledger. He realizes that every rule he writes in it becomes absolute law—enforced by reality itself. He begins to "fix" the city's moral decay with his own brand of absolute justice. Each episode features a new, bizarre rule and its visual consequences. To punish corrupt politicians, he writes: "Those who break promises will have their words manifest as chains." To stop theft, he writes: "Stolen money will weigh ten times its normal amount," causing a bank robber to be physically crushed by his own loot. He gains god-like control, but paranoia sets in. He soon discovers that someone else used the ledger before him—and that person is watching his every move, waiting for him to break his own rules.
    在腐败泛滥的城市，一位一丝不苟的底层官僚在旧档案室发现了一本古老的市政账簿。他震惊地发现，他在上面写下的每一条“规则”，都会瞬间成为现实世界的绝对法律。他开始用这种绝对正义来“修正”城市的道德沦丧。每集都是一条新规则的视觉奇观：为了惩罚不守信的政客，他写道“谎言将化为实体”，政客的嘴里吐出了束缚自己的锁链；为了制止盗窃，他写道“赃物重量翻倍”，导致抢劫犯在街头被自己背包里的钞票活活压垮。他成为了城市的“隐形上帝”，但很快发现这本账簿有前任主人。那个神秘人正躲在暗处，利用规则的漏洞布局，准备猎杀他并夺回神权。
    """,
    "搞笑": """The Last Human Male 最后的地球男人 
    概括： 病毒导致全球男性灭绝，男主因冷冻实验沉睡百年。醒来后发现世界由女性统治，作为唯一的男人，他成为了各方势力争夺的“珍稀资源”和“种族希望”，开启了被女帝、女将军争抢的求生之路。
    Tag: #Harem #PostApocalyptic #LastManStanding #FemaleDominance
     A genetic virus wipes out 99.9% of the male population. Adam, a pizza delivery guy frozen in a cryogenics lab accident in 2024, wakes up 100 years later. The world is now a high-tech matriarchy run by women, where men are extinct myths. When Adam is discovered, he becomes the most valuable asset on the planet. He is hunted by the Amazonian Warrior Queen who wants to breed a new army, and protected by a rebellious female scientist who sees him as a human being, not a tool. Adam, who was a loser in his old life, must now navigate a world where he is physically weaker but biologically essential. He uses his "ancient" knowledge (like how to fix a car or open a jar) to impress the powerful women, slowly building his own faction to restore balance to the world.
     一种针对Y染色体的病毒导致全球男性灭绝。2024年，送披萨的废柴亚当误入冷冻实验室被冰封。百年后他苏醒过来，发现世界已由女性绝对统治，男人成了历史书上的传说。作为地球上唯一的男人，亚当瞬间从屌丝变成了无价之宝。亚马逊女皇想抓他繁衍后代组建军队，反叛军女科学家想保护他研究解药。在这个女性体能和科技都碾压他的世界里，亚当成了各方势力争夺的“圣杯”。他利用旧世界的“直男技能”（比如修车、开瓶盖、讲土味情话）在这些强势女性中周旋，从一个被圈养的“种马”一步步成长为新世界的领袖，试图重建男女平等的秩序。
    """,
        "恐怖": """The Scream of the Statues 雕像的尖叫 
    概括：在未来，富人通过一种昂贵的药物实现了“永生”。女主是一名负责维护城市广场上历代伟人雕像的清洁工，直到她发现这些栩栩如生的“雕像”其实就是那些服药后的富人本人。
    Tag: #SciFiHorror #Dystopian #BodyHorror #Irony
    In a gleaming future city, death has been conquered by "Chronos," a drug affordable only to the ultra-rich. The drug halts cellular aging completely. The protagonist works as a low-level cleaner responsible for polishing the hundreds of hyper-realistic marble statues of "Ascended Ancestors" that line the city's boulevards. While cleaning a statue's face, she accidentally scratches its eye and sees a tear of fresh blood. The horrifying twist reveals the side effect of Chronos: it doesn't just stop aging; it exponentially slows down the user's perception of time until their physical body calcifies into living stone. The "statues" are not monuments; they are the immortal rich themselves, fully conscious, trapped in paralyzed bodies, screaming silently for centuries while pigeons defecate on them. The protagonist holds the secret that could topple the oligarchy: immortality is actually eternal imprisonment.
    在光鲜亮丽的未来都市，死亡已被一种名为“克洛诺斯”的昂贵药物攻克。只有顶级富豪才能享用它，实现细胞层面的“永生”。女主是一名底层清洁工，负责擦拭城市大道上数百尊栩栩如生的“飞升先祖”大理石雕像。某天，她在清洁一尊雕像的面部时，不小心划伤了它的眼睛，竟看到一滴鲜血流出。恐怖的真相揭开：药物的副作用并非停止衰老，而是将使用者的主观时间感无限拉长，导致肉体在物理层面逐渐钙化。广场上那些受人膜拜的“雕像”，其实就是那些服药后的富豪本人。他们并没有死，而是拥有了完全清醒的意识，却被困在石化的躯壳里，在漫长的岁月中承受着风吹日晒和鸟粪的羞辱，无声地尖叫了几个世纪。女主掌握了这个秘密：所谓的永生，其实是无期徒刑。

    The Pacer 陪跑员
    **概括：**职业陪跑员被富豪雇佣在私人庄园陪跑，日薪惊人。第三天他发现庄园四周都是高墙和摄像头，他和其他"陪跑员"实际是富豪狩猎游戏的猎物，必须在七天内逃出庄园否则会被猎杀。
    Tag: #MostDangerousGame #Survival #HumanHunting #Wealth
    Professional running coach Devon is hired by reclusive billionaire Mr. Zhao for a week-long "pacing job" at his private estate - $10,000 per day just to run alongside Zhao each morning. The estate is massive, scenic, isolated. Devon notices other "staff" - all athletic young men like him. On day three, Devon wakes to find his room locked from outside. An intercom activates: "The game begins. You have seven days to escape the estate. If we catch you, you lose." Devon discovers he and nine other men were hired under false pretenses - they're prey in a hunting game for Zhao and his wealthy friends. The hunters use tranquilizer darts, non-lethal weapons initially - it's about the chase, not the kill. But if you're caught, you're given a choice: permanent disappearance (paid off and silenced with blackmail insurance), or continue to the next round where weapons become lethal. 
    The estate spans 50 square miles of forest, rivers, and mountains. It's surrounded by a wall with sensors. Previous "employees" left warnings hidden in the woods: maps, safe zones, and a terrifying note: "Zhao always wins. He's done this 30 times." Devon must survive seven days, evade professional hunters with thermal drones and trained dogs, and find the one exit previous survivors hint at. But the hunters have a rule: the last man standing gets a special prize - a chance to become a hunter in the next game, plus $10 million. It turns survival into a competition where prey must betray each other.
    职业跑步教练Devon被隐居亿万富翁赵先生雇佣在他私人庄园进行为期一周的"配速工作"——每天1万美元只需每早陪赵跑步。庄园巨大、风景优美、孤立。Devon注意到其他"员工"——都是像他一样的运动型年轻男子。第三天，Devon醒来发现房间从外面锁住。对讲机激活："游戏开始。你有七天逃出庄园。如果我们抓住你，你输了。"Devon发现他和其他九个男人在虚假借口下被雇佣——他们是赵和富豪朋友狩猎游戏的猎物。猎人使用麻醉镖，最初是非致命武器——关于追逐，不是杀戮。但如果被抓，你会得到选择：永久失踪（用勒索保险封口收买），或继续下一轮武器变致命。庄园跨越50平方英里森林、河流和山脉。被带传感器的墙包围。以前的"雇员"在树林里留下警告：地图、安全区和可怕字条："赵总是赢。他做过30次。"Devon必须生存七天，躲避有热成像无人机和训练犬的专业猎人，找到以前幸存者暗示的唯一出口。但猎人有规则：最后站立的男人获得特殊奖——在下个游戏成为猎人的机会，加1000万美元。它把生存变成猎物必须互相背叛的竞争。
    
    The Cartographer's Curs 地图绘制师的诅咒
    概括：游戏世界架构师发现他在游戏中设计的灾难（瘟疫、地震）会在现实世界同步发生。当公司逼他设计一场毁灭城市的火山喷发时，他必须在48小时内对抗系统，修改注定降临的现实。
    Tag: #HighConcept #RealityBending #Thriller #CreatorVsCreation #MoralDilemma
    Liam, a lead world-builder for a massive MMORPG, is famous for his realistic disaster events. The horror begins with coincidences: he codes a plague for a virtual city, and a real village with the same name falls ill. He deletes a mountain range in-game, and a massive earthquake hits that exact coordinate in reality. When he tries to quit, the company forces him to design "more dynamic content"—a volcanic eruption that mirrors a real metropolis. He realizes the game isn't just simulating reality; it's dictating it. With only 48 hours before the event triggers, Liam tries to delete the code, but the system locks him out. He discovers previous architects all died mysteriously. The final twist: The game isn't creating the future; it's seeing it. He can't stop the disaster, but he can use the game's editor to change where it happens. He must race against time to redirect the catastrophe away from populated areas while the company tries to assassinate him to keep the "prophecy machine" running.
    利亚姆是一款大型网络游戏的首席世界架构师。诡异的巧合开始发生：他在游戏中设计了一场席卷虚拟城市的瘟疫，现实中一个同名村庄立刻爆发了未知疾病；他在游戏中“抹去”了一片山脉，现实中该区域便发生强烈地震。他意识到，自己的设计正在改写现实。 当他试图停手时，公司却逼迫他上线一个新版本：一场足以摧毁一座现实大都市的火山喷发。只有48小时，利亚姆试图删除代码，却发现系统拒绝修改——仿佛有某种意志在阻止他。调查发现前任架构师全部离奇死亡或失踪。最后一位留下的信息揭示了真相：“不是游戏改变现实，是游戏在‘看见’未来。”利亚姆无法阻止灾难，但他发现自己可以修改灾难的“坐标”。在公司杀手的追杀下，他必须在游戏服务器中展开一场代码追逐战，将即将降临现实的毁灭性灾难从城市中心移向无人荒野。
    """
}


# ==========================================
# 2. 核心 AI 适配引擎
# ==========================================

def call_ai_engine(provider, api_key, model_name, prompt, retries=3):
    for i in range(retries):
        try:
            safe_prompt = str(prompt)
            if provider == "Gemini":
                client = genai.Client(api_key=api_key)
                config = None
                if "gemini-3" in model_name:
                    level = types.ThinkingLevel.HIGH if "pro" in model_name else types.ThinkingLevel.MEDIUM
                    config = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level=level))
                response = client.models.generate_content(model=model_name, contents=safe_prompt, config=config)
                return response.text if (response and response.text) else "❌ AI 返回空内容"

            elif provider == "GPT (OpenAI)":
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(model=model_name,
                                                      messages=[{"role": "user", "content": safe_prompt}])
                return resp.choices[0].message.content

            elif provider == "Claude (Anthropic)":
                client = anthropic.Anthropic(api_key=api_key)
                resp = client.messages.create(model=model_name, max_tokens=8000,
                                              messages=[{"role": "user", "content": safe_prompt}])
                return resp.content[0].text

            elif provider == "OpenRouter":
                # 使用 OpenAI SDK 初始化 OpenRouter 的客户端
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                # 发起带有 Reasoning 启用的单次完整请求
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": safe_prompt}],
                    extra_body={"reasoning": {"enabled": True}}
                )
                # 直接提取并返回模型的最终响应内容
                return resp.choices[0].message.content

        except Exception as e:
            err = str(e)
            if ("503" in err or "429" in err) and i < retries - 1:
                time.sleep((i + 1) * 5)
                continue
            return f"❌ 接口报错: {err}"
    return "❌ 服务器持续繁忙。"


# ==========================================
# 3. 网页交互界面
# ==========================================

st.title("🎬 短剧 AI 创意生产")
st.caption("版本：20126_v5 | 批量生成 30 个创意 | 完整展示 Top 5 筛选结果")

with st.sidebar:
    st.header("⚙️ 引擎配置")
    provider = st.selectbox("选择厂商", ["Gemini", "GPT (OpenAI)", "Claude (Anthropic)", "OpenRouter"])
    models_map = {
        "Gemini": ["gemini-3-flash-preview", "gemini-3-pro-preview", "gemini-3.1-pro-preview"],
        "GPT (OpenAI)": ["gpt-4o", "gpt-4o-mini"],
        "Claude (Anthropic)": ["claude-3-5-sonnet-20240620"],
        "OpenRouter": ["anthropic/claude-opus-4.6",
                      "anthropic/claude-sonnet-4.6",
                      "anthropic/claude-sonnet-4",
                      "anthropic/claude-3.5-haiku",
                      "anthropic/claude-3.7-sonnet",
                      "anthropic/claude-3.5-sonnet",
                      "anthropic/claude-sonnet-4.5",
                      "anthropic/claude-haiku-4.5",
                      "anthropic/claude-opus-4.5",
                      "gemini-3-flash-preview",
                      "gemini-3-pro-preview",
                      "gemini-3.1-pro-preview",
                      "gpt-4o",
                      "gpt-4o-mini"]  # 绑定你需要的模型
    }
    model_name = st.selectbox("选择具体型号", models_map[provider])
    api_key = st.text_input(f"输入 {provider} Key", type="password")

col_l, col_r = st.columns([1, 2])

with col_l:
    st.subheader("1. 创作与修改设定")
    theme_btn = st.selectbox("题材选择", list(SUCCESS_CASES.keys()))
    theme_custom = st.text_input("其他题材 (AAA)", placeholder="填入将替换主题")
    active_theme = theme_custom if theme_custom else theme_btn

    # --- A. 立即生成按钮 (30个) ---
    if st.button("🚀 立即生成创意 (30个)", use_container_width=True):
        if not api_key:
            st.error("请先输入 API Key")
        else:
            with st.spinner(f"正在创作 30 个创意..."):
                p1 = f"{IDENTITY}\n任务：写 30 个{active_theme}短剧创意。\n{STRICT_FORMAT_10}"
                draft = call_ai_engine(provider, api_key, model_name, p1)

                if draft and "❌" not in draft:
                    time.sleep(1)
                    p2 = f"作为严格的审查官，确保以下 30 个创意符合五行结构，每项必须包含“概括：”前缀。只输出内容：\n{draft}\n{STRICT_FORMAT_10}"
                    st.session_state['res'] = call_ai_engine(provider, api_key, model_name, p2)
                    st.session_state['theme'] = active_theme
                    st.session_state['is_custom'] = bool(theme_custom)
                    if 'filtered_res' in st.session_state: del st.session_state['filtered_res']
                else:
                    st.error(draft)

    # --- B. 针对性精修 (同步修改 30 个) ---
    if 'res' in st.session_state:
        st.write("---")
        st.write("🔧 针对性精修 (同步修改 30 个创意):")
        m1, m2, m3 = st.columns(3)


        def run_refine(label):
            lookup = "自定义" if st.session_state.get('is_custom') else st.session_state['theme']
            case = SUCCESS_CASES.get(lookup, "")
            p_ref = f"""参考案例：{case}。针对以下 30 个创意执行【{label}】修改。

            [硬性准则]：
            1. 每一项必须以“剧名”开头，第二行必须包含“概括：”。
            2. 严禁出现 Title/Plot 等标签。
            3. 依然输出 30 个，保持完整五行结构。

            内容：\n{st.session_state['res']}\n{STRICT_FORMAT_10}"""

            with st.spinner(f"正在进行{label}修改..."):
                st.session_state['res'] = call_ai_engine(provider, api_key, model_name, p_ref)
                if 'filtered_res' in st.session_state: del st.session_state['filtered_res']
                st.rerun()


        if m1.button("增加趣味"): run_refine("增加趣味")
        if m2.button("更加简单"): run_refine("更加简单")
        if m3.button("增加冲击"): run_refine("增加冲击")

        # --- C. 智能筛选按钮 (Top 5 完整版) ---
        st.write("---")
        st.write("🎯 智能评估与筛选:")
        if st.button("📊 筛选前 5 名 (完整展示)", use_container_width=True):
            with st.spinner("正在挑选 Top 5 爆款潜力作品并准备完整内容..."):
                filter_p = f"""
                你是一个非常擅长的创意筛选和数据分析的编剧，可以根据[过往的爆款创意和喜爱度排名]，挑选出生成的创意中最符合过往爆款创意特征的创意，保证挑选出用户喜爱度最高的创意
                作为短剧制片人，请从以下 30 个创意中评估其爆款潜力，选出得分最高的 5 个。

                [核心要求]
                1. 必须完整输出这 5 个选中的创意（包括剧名、概括、Tag、英文内容、中文内容）。
                2. 严格保持每个创意的五行结构，确保每项都包含“概括：”和“Tag:”标签。
                3. 严禁添加任何额外标识、分数值、百分比或评价文字。
                4. 只输出选中的 5 个创意的完整内容。
                
                [你的任务]
                在这些创意中根据过往的爆款创意和喜爱度排名对比，识别爆款特征
                1. 挑选出生成的创意中最符合过往爆款创意标准的前5个创意
                2. 仅挑选，而不作任何创意修改
                
                [过往的爆款创意和喜爱度排名]
                喜爱度：80%
                Prophecy of Doom剧透之眼 
                概括：女主能看到每个人头顶漂浮的“结局字幕”（例如：‘将于3年后死于癌症’）。她一直过着消极避世的生活，直到她遇见了一个头顶字幕显示为“将毁灭世界”的男人，而这个男人正在追求她。
                Tag: #RomanceThriller #SupernaturalMystery #FateVsFreeWill #HighStakes
                Maya suffers from a burdensome gift: she sees floating text above everyone's head revealing their ultimate fate or cause of death. "Divorced at 40," "Hit by a bus next Tuesday." This knowledge has made her cynical and detached, avoiding close relationships to spare herself the pain. Her life changes when she meets Noah, a charming, kind-hearted philanthropist who seems perfect in every way. However, the text above his head reads: "Will Destroy the World in 365 Days." Terrified but intrigued, Maya decides to date him, not for love, but to figure out how this gentle man triggers the apocalypse—and to stop him. As she falls for him, she realizes the prophecy is self-fulfilling: the very actions she takes to prevent the catastrophe might be exactly what pushes him toward his dark destiny.
                玛雅背负着一个沉重的诅咒：她能看到每个人头顶漂浮的“结局字幕”，揭示他们的最终命运或死因。比如“40岁离婚”、“下周二死于车祸”。这种能力让她变得冷漠避世，不敢与人建立亲密关系。直到她遇见了诺亚，一个迷人、善良的慈善家。然而，诺亚头顶的字幕却显示：“将于365天后毁灭世界”。出于恐惧和好奇，玛雅决定接受他的追求，不是为了爱，而是为了潜伏在他身边，搞清楚这个温柔的男人如何引发末日，并阻止他。然而，随着她不可自拔地爱上他，她发现这是一个自我实现的预言：她为了阻止灾难所做的一切努力，似乎正是将诺亚推向黑暗命运的推手。
                
                喜爱度：73%
                The Blind Wife's Secret 盲妻的秘密
                概括：女主在一场事故中失明，她的丈夫却把情妇带回家，以为她看不见而在她面前肆无忌惮地亲热。殊不知，女主的视力早已恢复，她选择继续装瞎，只为收集证据，策划一场让渣男身败名裂的完美复仇。
                Tag: #Revenge #CheatingHusband #FakeBlindness #ThrillerRomance#StrongFemaleLead
                After a car accident leaves her blind, Sarah becomes entirely dependent on her husband, Mark. However, Mark is not the devoted spouse he pretends to be. He moves his mistress into their home under the guise of a "nurse" and flaunts their affair right in front of Sarah's unseeing eyes. But here is the twist: Sarah’s vision returned two weeks ago.
                Every day is a torture of acting; she must endure the humiliation of hearing and vaguely seeing them together without reacting. She installs hidden cameras, gathers financial documents, and slowly transfers assets while playing the role of the helpless invalid. The climax builds to their anniversary party, where Mark plans to have Sarah declared mentally incompetent to seize her inheritance. Instead, Sarah walks onto the stage, eyes clear and focused, and plays a video that shocks the entire elite society, turning the hunter into the prey.
                在一场车祸导致失明后，莎拉变得完全依赖她的丈夫马克。然而，马克并非他伪装的那样深情。他以“护士”的名义将情妇接进家中，并以为莎拉看不见，竟在她面前公然调情。但反转来了：莎拉的视力在两周前就已经恢复了。
                每一天对她来说都是一场演技的考验；她必须忍受着羞辱，看着那对狗男女在眼皮底下亲热却不能有任何反应。她暗中安装了针孔摄像头，收集财务造假证据，并趁着扮演“无助废人”的时候悄悄转移资产。高潮发生在他们的结婚纪念日晚宴上，马克原本计划宣布莎拉精神失常以夺取她的遗产。然而，莎拉目光清澈地走上舞台，在大屏幕上播放了一段令全场名流震惊的视频，瞬间将猎人变成了猎物。
                
                
                喜爱度：72%
                The Fortune Teller of Beverly Hills 比佛利山庄的算命师
                概括：华裔占卜师预见男神影星将死而违例护他，揭穿经纪人与恶魔交易制造“意外”的阴谋，并在群魅汇聚的洛城接受“超自然守护者”的命运。
                Tag：#Young Women #Supernatural Romance #Live-Action Short Drama
                Chinese-American fortune teller Mei Chen runs a small shop in Beverly Hills, using real mystical abilities inherited from her grandmother while pretending to be a fraud. When Hollywood heartthrob Ryan Matthews visits as a joke for a movie role, she accidentally sees his death in three months. Despite her rule against interfering with fate, she becomes his "spiritual advisor," secretly protecting him from increasingly bizarre accidents while teaching him Eastern philosophy. Their sessions turn intimate as Ryan discovers Mei's readings about his past are impossibly accurate. Soon, Mei uncovers a dark secret: Ryan's manager has been orchestrating the accidents, having made a demonic deal for his fame. As Mei's powers attract other mystical beings to LA, she must choose between hiding or embracing her role as the city's supernatural guardian.
                华裔算命师陈玫在比佛利山庄经营着一家小店。她继承了祖母的神秘能力，却一直伪装成骗子以躲避关注。当好莱坞男神瑞恩·马修斯为体验角色而来访时，她意外看到了他三个月后的死亡画面。尽管有不干涉命运的规矩，她还是无法坐视不理，于是成为了他的“精神导师”，在教他东方哲学的同时，暗中保护他免受一系列离奇意外的伤害。随着瑞恩发现陈玫对他过去的解读惊人地准确，他们的关系也愈发亲密。然而，陈玫很快发现这些“意外”是瑞恩的经纪人一手策划的，他为了瑞恩的名声与恶魔做了交易。当陈玫的能力吸引来洛杉矶其他的神秘生物时，她必须选择是继续隐藏，还是接受自己作为城市超自然守护者的命运。
                
                喜爱度：70%
                Mirror Signal 镜子里的陌生人
                概括：一位时尚博主发现自己被车祸后昏迷的真实自我替代，成为AI替身为药企赚钱，通过反射世界发出求救信号，最终依靠粉丝的帮助寻找自我救赎。
                Tag: #MirrorSignal #DigitalTrap #AIvsHuman
                A perfectionist fashion blogger live-streams makeup tutorials every morning to her 2 million followers. One day, she notices her mirror reflection has a 0.5-second delay. At first, she assumes it's a defective mirror.
                But the reflection begins "disobeying"—when she smiles, it frowns; when she speaks, the lip movements don't sync. Panicked, she smashes all the mirrors. Yet when taking a phone selfie, she sees herself on screen silently crying for help.
                The brutal truth emerges: three years ago, she was in a car accident and fell into a vegetative coma. The current "her" is an AI generated from social media data, continuing to run her account to profit a pharmaceutical company. The real her is trapped in consciousness, sending distress signals through reflections.
                It turns out that one of her followers is a neuroscientist who recognizes the truth. The digital rescue operation begins...
                完美主义的时尚博主每天早晨对着镜子直播化妆教程，拥有200万粉丝。某天她发现镜中的自己动作出现0.5秒延迟，起初以为是镜子问题，但逐渐发现镜中人开始"不听指挥"——她微笑时镜中人皱眉、她说话时镜中人嘴型不同步。恐慌中她砸碎所有镜子，却在手机自拍时看到屏幕里的自己正在无声哭泣求救。真相残酷揭晓：三年前她遭遇车祸植物人昏迷，现在的"她"是AI根据社交媒体数据生成的数字替身，在继续运营账号为医药公司赚钱；而真正的她被困在意识里，只能通过镜像世界发出求救信号。最后反转：她的粉丝中有一个神经科学家识破真相，开始策划"数字救援"。
                
                喜爱度：70%
                The Sleep Factory 睡眠工厂
                概括：卡洛斯发现梦境劳动在为富人建数字天堂并准备迁移精英意识，遂在虚拟监狱内发动起义阻止终极剥削
                Tag: #Sci-Fi#Dream Exploitation#Consciousness Enslavement#Virtual Labor#Spiritual Liberation
                In 2094, human sleep becomes industrialized through the Morpheus Corporation's dream labor system. Citizens work double shifts—eight hours awake in reality, eight hours asleep in virtual factories where their subconscious minds perform complex tasks like data processing, creative design, and problem-solving for corporate clients. The wealthy purchase premium rest while the poor are trapped in endless dream labor, their minds never truly resting. Dream worker Carlos Martinez discovers his daughter has been enrolled in child sleep labor programs, her developing brain exploited to generate corporate profits during what should be restorative sleep. When Carlos investigates, he uncovers that the corporation is using dream workers to build a virtual world where only the elite will live while the masses remain trapped in perpetual sleep slavery. The dream factories are actually constructing a digital paradise for the wealthy, powered by the enslaved minds of sleeping workers. Carlos must organize dream laborers to rebel from within their virtual prisons before the corporation implements the final phase—transferring the consciousness of the elite into the completed digital realm while leaving physical bodies behind to work eternally in sleep.
                在2094年，人类睡眠通过墨菲斯公司的梦境劳动系统被工业化。公民进行双班工作——现实中清醒八小时，在虚拟工厂中睡眠八小时，他们的潜意识为企业客户执行数据处理、创意设计和问题解决等复杂任务。富人购买优质休息，而穷人被困在无尽的梦境劳动中，他们的思维从未真正休息。梦境工人卡洛斯·马丁内斯发现他的女儿被注册到儿童睡眠劳动项目中，她发育中的大脑在应该恢复性睡眠期间被剥削来产生企业利润。当卡洛斯调查时，他揭露公司正在使用梦境工人建造一个只有精英居住的虚拟世界，而大众仍被困在永久睡眠奴役中。梦境工厂实际上在为富人建造数字天堂，由睡眠工人的被奴役思维提供动力。卡洛斯必须组织梦境劳动者从他们的虚拟监狱内部反叛，在公司实施最终阶段之前阻止他们——将精英的意识转移到完成的数字领域，同时留下物理身体永远在睡眠中工作。
                
                喜爱度：70%
                The Future Lens 未来镜头
                概括：能拍到未来灾祸的相机让记者成名，他发现“喜事”被另一台相机独占，遂寻找偷走明日快乐的人
                Tag：#Time Travel #Photography #Supernatural #Empowerment#Visual Spectacle
                A photojournalist discovers a camera that captures events 24 hours in the future. Each episode features him photographing everyday disasters with shocking twists: a businessman's coffee cup exploding and burning his face off, escalator steps suddenly reversing and crushing shoppers, a jogger being swallowed by a sinkhole that opens beneath her feet, office windows shattering inward during a board meeting, a family barbecue where the grill erupts like a volcano. He gains fame predicting these bizarre accidents, but gradually realizes the camera only shows disasters because someone else is using an identical camera to photograph all the good things that happen tomorrow. The previous owner left a note: "There are two cameras - one sees light, one sees darkness. I chose wrong." Now he must find his mysterious counterpart who's been stealing all of tomorrow's joy.
                一位摄影记者发现了一台能拍摄未来24小时事件的相机。每集都有他拍摄日常灾难的惊人扭转：商人的咖啡杯爆炸烧毁他的脸，自动扶梯台阶突然倒转碾压购物者，慢跑者被脚下突然张开的天坑吞没，董事会议期间办公室窗户向内爆裂，家庭烧烤时烤架像火山般喷发。他因预测这些诡异事故而成名，但逐渐意识到相机只显示灾难，是因为另一个人正在用同样的相机拍摄明天发生的所有好事。前任主人留下纸条："有两台相机——一台看见光明，一台看见黑暗。我选错了。"现在他必须找到那个一直在偷走明日所有快乐的神秘对手。
                
                喜爱度：68%
                The Scream of the Statues 雕像的尖叫 
                概括：在未来，富人通过一种昂贵的药物实现了“永生”。女主是一名负责维护城市广场上历代伟人雕像的清洁工，直到她发现这些栩栩如生的“雕像”其实就是那些服药后的富人本人。
                Tag: #SciFiHorror #Dystopian #BodyHorror #Irony
                In a gleaming future city, death has been conquered by "Chronos," a drug affordable only to the ultra-rich. The drug halts cellular aging completely. The protagonist works as a low-level cleaner responsible for polishing the hundreds of hyper-realistic marble statues of "Ascended Ancestors" that line the city's boulevards. While cleaning a statue's face, she accidentally scratches its eye and sees a tear of fresh blood. The horrifying twist reveals the side effect of Chronos: it doesn't just stop aging; it exponentially slows down the user's perception of time until their physical body calcifies into living stone. The "statues" are not monuments; they are the immortal rich themselves, fully conscious, trapped in paralyzed bodies, screaming silently for centuries while pigeons defecate on them. The protagonist holds the secret that could topple the oligarchy: immortality is actually eternal imprisonment.
                在光鲜亮丽的未来都市，死亡已被一种名为“克洛诺斯”的昂贵药物攻克。只有顶级富豪才能享用它，实现细胞层面的“永生”。女主是一名底层清洁工，负责擦拭城市大道上数百尊栩栩如生的“飞升先祖”大理石雕像。某天，她在清洁一尊雕像的面部时，不小心划伤了它的眼睛，竟看到一滴鲜血流出。恐怖的真相揭开：药物的副作用并非停止衰老，而是将使用者的主观时间感无限拉长，导致肉体在物理层面逐渐钙化。广场上那些受人膜拜的“雕像”，其实就是那些服药后的富豪本人。他们并没有死，而是拥有了完全清醒的意识，却被困在石化的躯壳里，在漫长的岁月中承受着风吹日晒和鸟粪的羞辱，无声地尖叫了几个世纪。女主掌握了这个秘密：所谓的永生，其实是无期徒刑。
                
                喜爱度：68%
                The 101st Divorce 第101次离婚
                概括：丈夫为救深陷死亡循环的妻子而假意绝情逼离，得知真相的妻子撕毁离婚协议，二人利用百次轮回记忆联手对抗必死宿命。
                Tag: #TimeLoop #EmotionalRedemption
                Anna is trapped on the day she signs her divorce papers. Every time she signs and walks out of the building, she dies in a bizarre accident — a car crash, a falling object, even a stray bullet. Her husband, Ryan, is cold and cruel that day, forcing her to “just sign it and get out of my life. By the tenth loop, Anna breaks down and tries to stab Ryan before signing. Without even looking up, he catches the blade and says coldly, “You tried that in loop twelve. It doesn’t work. No matter what you do — you’ll die at 10:05.”
                Anna freezes. She’s not the only one who remembers. Ryan does too. The real curse isn’t the divorce — it’s Anna’s destined death. Ryan accidentally gained the ability to reset time. For 99 loops, he tried everything: to love her, to protect her, to run away with her… but she always died in his arms. By the 100th loop, he realized the only escape: sever their bond completely. If Anna can hate him enough to leave the city before 10 a.m., she might escape death. His cruelty, his coldness — all of it was an act to push her away and save her life.
                But when Anna learns the truth, she tears up the divorce papers and says,“Then this time, we don’t run. If we die, we die together. If we live, we live together.” Using Ryan’s hundred loops of “death maps,” the two join forces to confront the fate that has hunted them like death itself.
                安娜被困在了签署离婚协议的那一天。每次她签完字走出大楼，都会遭遇各种离奇意外身亡（车祸、高空坠物、甚至被流弹击中）。丈夫瑞恩在这一天表现得冷酷无情，逼她“赶紧签字，滚出我的生活”。 安娜在第10次循环中崩溃发疯，试图在签字前捅死瑞恩。然而，瑞恩头也不抬地接住了她刺来的刀，冷冷地说：“这招你在第12次循环用过了，没用。无论我死不死，你都会在10点05分准时死掉。”
                安娜震惊地发现，拥有记忆的不仅是她，还有瑞恩。 原来，真正的诅咒是“安娜必死”，而瑞恩偶然获得了重置时间的能力。前99次循环，瑞恩尝试过爱她、保护她、带她私奔，结果安娜都死在了他怀里。 第100次，他绝望地发现唯一的生路是：彻底斩断两人的因果。只要安娜在10点前恨透他并彻底离开这座城市（不签字，直接逃离），或许能躲过死神。他所有的冷漠和羞辱，都是为了逼她在那一刻转身离开，而不是签字。
                得知真相的安娜没有逃离。她撕碎了离婚协议，对那个疲惫不堪的男人说：“这一次，我们谁都不走。要死一起死，要活一起活。”两人利用瑞恩百次循环积累的“死亡地图”，联手对抗死神来了般的宿命。
                
                喜爱度：68%
                The Amnesiac's Diary 失忆者的日记
                概括：失忆妻在“完美总裁丈夫”照料下发现自写日记的求救警示，被迫白天演妻子夜里寻真相，追溯车祸与逃生计划。
                Tag: # High-Suspense # Thriller # Angst
                Mia wakes from a car crash with severe amnesia. By her side is her handsome, perfect, and loving husband, CEO Liam, who patiently helps her 'remember' their idyllic life. However, Mia discovers a locked diary in her own handwriting. The first page reads: "If you lose your memory, do not trust Liam. He is a monster. Escape at all costs." Mia is thrown into a spiral of terror. Is the gentle man beside her real, or is the monster in the diary? She's forced to live a double life: by day, the loving, dependent wife; by night, following the diary's clues to uncover the truth about her past, her escape plan, and the real cause of her 'accidental' crash.
                Mia在一场车祸后严重失忆。她醒来时，身边是她英俊、完美、且充满爱意的丈夫, 集团总裁Liam。Liam无微不至地照顾她，帮她回忆两人甜蜜的过去。然而，Mia却在家中发现了一本上锁的日记，里面是她自己的笔迹，而日记的第一页写着：“如果你失忆了，不要相信Liam。他是个怪物。不惜一切代价逃离他。” Mia陷入了巨大的恐惧。她眼前这个温柔的男人，和日记中那个可怕的恶魔，到底哪一个才是真的？她被迫上演“双面人生”：白天，她是那个依赖丈夫的失忆妻子；晚上，她则根据日记的线索，试图拼凑出自己计划逃跑的真相，以及这场“意外”车祸的真正原因。
                
                喜爱度：68%
                The Time Mercenary 时间佣兵
                概括：携战术AI穿梭历史纠偏的佣兵在一次阻止灭世刺杀的行动里意识到，最大篡改者正是雇主时间局本身。
                Tag: #Time Travel #Mercenary #Historical Revision #AI Paradox #Combat
                Veteran soldier Kai is recruited by a future-based Time Bureau to become a time mercenary alongside tactical AI Keke. Keke calculates timeline fluctuation rates, provides historical context, and runs tactical simulations. Their mission: traverse time to stop “time criminals” attempting to alter history. Kai relishes the thrill of crushing ancient armies with futuristic technology, but the AI constantly warns him that their actions are creating unpredictable “time paradox ripples.” When they're sent to prevent a pivotal assassination that leads to human extinction, Kai discovers that their employer, the Time Bureau itself, may be history's greatest manipulator.
                退伍兵“凯”被一个来自未来的时间管理局招募，成为携带战术AI“刻刻”的时间佣兵。“刻刻”能计算时间线变动率、提供历史背景和战术模拟。他们的任务是穿越时空，阻止各种试图篡改历史的“时间罪犯”。凯享受着用未来科技碾压古代军队的快感，但AI不断警告他行动正在造成不可预知的“时间悖论涟漪”。当他们被派去阻止一场导致人类灭绝的关键刺杀时，凯发现雇主时间管理局本身可能就是历史最大的篡改者。
                
                喜爱度：68%
                The Historical Rewriter 历史重写者
                概括：能附身名人的学渣每改一次历史现世更糟，最终自我回溯同步修正学会接受必要之痛
                Tag：#Time Travel #Historical Figures #Titanic
                Jake, a failing history student, discovers he can temporarily inhabit historical figures at crucial moments and change their outcomes. He saves the Titanic but accidentally preserves a passenger who becomes a dangerous dictator. Preventing Lincoln's assassination triggers a more brutal civil war. Helping Tesla promote wireless technology creates an early surveillance state. Each "fix" creates worse unintended consequences in the present. Jake discovers his power comes from an ancient artifact that feeds on historical chaos - the more he changes, the more unstable reality becomes. In the climax, he must simultaneously inhabit multiple historical figures to undo his changes, learning that some tragedies, while painful, were necessary stepping stones for humanity's growth and progress.
                杰克是一个成绩糟糕的历史系学生，发现自己可以暂时附身历史人物，在关键时刻改变结局。他拯救了泰坦尼克号但意外保存了一个成为危险独裁者的乘客。阻止林肯遇刺引发了更残酷的内战。帮助特斯拉推广无线技术创造了早期监控国家。每次"修复"都在现实中造成更糟的意外后果。杰克发现他的能力来自一个以历史混乱为食的古器物——他改变得越多，现实就越不稳定。在高潮中，他必须同时附身多个历史人物来撤销改变，学会一些悲剧虽然痛苦，但是人类成长和进步的必要垫脚石。
                
                喜爱度：68%
                The Rule Writer 规则书写者
                概括：官僚写进古账簿的条文会变现实，他用“绝对正义”净化城市却察觉幕后还有先行者监视
                Tag：#Supernatural #Mystery #AI Empowerment #Visual Spectacle
                In a city drowning in corruption, a meticulous bureaucrat discovers that every rule he writes in an ancient municipal ledger becomes absolute law—enforced by reality itself. He begins to "fix" the city's moral decay with his own brand of absolute justice. Each episode is a new, bizarre rule. To punish corrupt politicians, he writes: "Those who break their promises will have their words manifest as chains that bind them." To stop theft, he writes: "Stolen money will physically weigh ten times its normal amount," causing a bank robber to be crushed by his own loot. Soon he discovers that someone else has been using the ledger before him, and that person is watching his every move. 
                在一个腐败泛滥的城市里，一位一丝不苟的官僚发现，他在一本古老市政账簿上写下的每一条规则都会成为绝对法律——由现实本身执行。他开始用自己那套绝对正义的方式来"修正"城市的道德沦丧。每一集都是一条新的、奇异的规则。为了惩罚腐败的政客，他写道："那些违背承诺的人，他们的话语将显化为束缚自己的锁链。"为了制止盗窃，他写道："被盗的钱财，其物理重量将变为正常的十倍，"导致一个银行劫匪被自己的赃物压垮。很快他发现，在他之前就有人使用过这本账簿，而那个人正在暗中观察着他的一举一动。
                
                喜爱度：68%
                Codename: Zero 代号：零
                概括：被组织背叛的顶级特工“零”化名工人隐居，妹妹被黑帮绑架后重拾杀技，单枪匹马摧毁地下势力掀起复仇风暴。
                Tag: #Male-Oriented #Secret Agent #Gangster
                He was a shadow known only as "Zero," the nation's most dangerous black-ops agent. Betrayed and abandoned by his organization during a mission, he was presumed dead. Three years later, living under the guise of an ordinary dock worker, he wants only a peaceful life to protect his younger sister. But constant harassment from a local gang and his sister's eventual kidnapping ignites his fury. They picked the wrong man. The former top agent is forced to revive his dormant lethal skills. Answering to no one but himself, he wages a one-man war, dismantling the city's entire underworld hierarchy from the street thugs to the mastermind behind it all. The world will be reminded of the terror inspired by the name "Zero." 
                他是为国家执行最危险任务的影子，代号“零”。在一次任务中被组织背叛、抛弃后，所有人都以为他已经死了。三年后，伪装成一个普通码头工人的他，只想平静地生活，守护唯一的妹妹。但当地黑帮的不断骚扰，和他妹妹的意外被绑，彻底点燃了他的怒火。他们惹错了人。这位曾经的顶级特工，被迫重拾尘封的杀戮技能。他不再为任何人效力，只为自己而战。从街头混混到幕后黑手，他将以一己之力，掀翻整个城市的地下秩序。全世界都将再次记起，那个被称作“零”的男人到底有多么恐怖。
                
                
                喜爱度：67%
                The Vanishing Roommate 消失的室友
                概括： 女主和一名完美的室友合租了一年，两人情同姐妹。某天回家，室友的所有东西都不见了，仿佛从未存在过。女主报警，警方却查出这间公寓过去五年一直只有女主一人的居住记录。更恐怖的是，女主手机里两人的合照，现在只剩下她一个人对着空气笑。
                Tag: #PsychologicalThriller #Mystery #Gaslighting #PlotTwist #UrbanLegend
                Emily has lived with her perfect roommate, Chloe, for a year. They share clothes, secrets, and memories. One day, Emily comes home to find the apartment empty—Chloe's stuff is gone. She calls the police, only to be told that according to all records, Emily has lived alone for the past five years. There is no record of a "Chloe." Even worse, when Emily checks her phone gallery, photos of the two of them now show Emily hugging thin air. Is Emily crazy? Is Chloe a ghost? Or is there a darker, government-level experiment erasing people from existence?
                艾米丽和完美的室友克洛伊合租了一年，她们分享衣物、秘密和记忆。某天艾米丽回家，发现公寓空了——克洛伊的所有物品凭空消失。她报警求助，却被告知根据所有房屋租赁和监控记录，过去五年这间公寓只有艾米丽一人居住。查无此人。更恐怖的是，当艾米丽翻看手机相册，曾经两人的亲密合照，现在变成了她一个人对着空气拥抱。是艾米丽疯了？克洛伊是鬼魂？还是说，有一场更黑暗的、关于“抹除存在”的实验正在进行？
                
                喜爱度：65%
                The Seven-Day Widow 七日遗孀
                概括： 被宣布"意外身亡"的富豪妻子获得七天"死亡假期"调查真相，发现丈夫、闺蜜和婆婆联手谋杀她争夺遗产，于是在自己的葬礼上复活反杀。
                Tag: #Revenge #FakeDeath #Betrayal #TwistedComeBack #StrongFemaleLead
                Victoria Sterling "dies" in a yacht explosion. But she wakes up in a hospital morgue with a mysterious note beside her: "You have 7 days before your death becomes permanent. Find the truth."
                Disguised and presumed dead, Victoria infiltrates her own funeral preparations. She watches her "grieving" husband flirt with her best friend over champagne. She sees her mother-in-law already redecorating her bedroom. She discovers a fifty-million-dollar life insurance policy signed just three days before her "accident."
                Each day reveals another betrayal. Day 3: her husband hired the bomber. Day 5: her best friend has been sleeping with him for years. Day 6: her own mother sold her out to cover gambling debts.
                On Day 7, at her lavish funeral attended by high society, Victoria walks in wearing her burial dress. "Sorry I'm late to my own party." She has the evidence, the lawyers, and a very detailed prenup they all conveniently forgot about.
                维多利亚·斯特林在一场游艇爆炸中"身亡"。但她在医院太平间醒来，身边有一张神秘纸条："你有七天时间，否则死亡将成为永久。找出真相。"
                伪装起来、被认定已死的维多利亚潜入了自己的葬礼筹备现场。她看着"悲痛欲绝"的丈夫与她最好的闺蜜举杯调情。她看见婆婆已经在重新装修她的卧室。她发现一份五千万美元的人寿保险，签署日期就在她"意外"发生的三天前。
                每一天都揭露出另一层背叛。第三天：她丈夫雇佣了炸弹手。第五天：她闺蜜和他偷情多年。第六天：她亲生母亲为了填补赌债出卖了她。
                第七天，在名流云集的奢华葬礼上，维多利亚身穿入殓礼服走了进来。"抱歉，我的派对来晚了。"她手握证据、律师，以及一份他们都"恰好"忘记的详尽婚前协议。
                
                喜爱度：65%
                The Vanished Wife & The Mystery Heiress 消失的妻子与神秘继承人
                概括： 遭受丈夫背叛和谋杀未遂的家庭主妇，整容后以神秘亿万富翁继承人的身份归来。她步步为营，诱惑前夫爱上新的自己，只为在婚礼当天揭露真相，夺走他的一切。
                Tag: #Revenge #IdentitySwap #CheatingHusband #FemaleEmpowerment #PsychologicalThriller
                Clara was the perfect, submissive housewife until she overheard her husband, James, plotting to kill her for her life insurance money to pay off his gambling debts. Narrowly escaping a staged car accident, Clara is rescued by a reclusive billionaire who sees her potential. She undergoes reconstructive surgery and intense training, emerging as "Vivian," a sophisticated and ruthless venture capitalist.
                Two years later, Vivian returns to the city to acquire James's failing company. James, unaware that this stunning woman is the wife he thinks is dead, falls madly in love with her—and her fortune. Vivian plays a dangerous game of cat and mouse, seducing him while systematically destroying his life from the shadows. But as the final trap is set for their "wedding day," James begins to notice familiar habits in Vivian. The tension peaks when Vivian hands him a wedding gift: the brake line she cut from her own car two years ago.
                克拉拉曾是一个完美、顺从的家庭主妇，直到她无意中听到丈夫詹姆斯密谋为了骗取巨额保险金偿还赌债而杀害她。在一场人为制造的车祸中死里逃生后，克拉拉被一位隐居的亿万富翁救下。经过整容手术和高强度的训练，她摇身一变，成为了“薇薇安”——一位精致而无情的风险投资家。
                两年后，薇薇安回到这座城市，收购了詹姆斯濒临破产的公司。詹姆斯完全没有意识到眼前这位绝世美女就是他以为已经死去的妻子，他疯狂地爱上了她——以及她的财富。薇薇安玩起了一场危险的猫鼠游戏，在引诱他的同时，暗中系统性地摧毁他的生活。但在为他们“婚礼当天”设下最后陷阱时，詹姆斯开始在薇薇安身上注意到一些熟悉的习惯。当薇薇安递给他一份结婚礼物——两年前她从自己车上剪下的刹车线时，剧情的张力达到了顶峰。
                
                喜爱度：65%
                The Shutter of Tomorrow 明日快门
                概括：一部能拍出“未来关键瞬间”的宝丽来相机，让一个愤世嫉俗的记者一夜成名。但当她拍下一张显示城市将被大火吞噬的照片时，她发现照片中的“纵火犯”竟是未来的自己。
                Tag: #HighConcept, #Sci-FiThriller, #TimeParadox, #MoralDilemma
                Maya, a cynical tabloid reporter struggling to expose real truths, stumbles upon an old Polaroid camera. She soon discovers it doesn't capture the present, but rather the single most "decisive future moment" of its subject. She uses it to pre-emptively expose a mayor's corrupt deal and saves countless investors by photographing a stock's future crash. She becomes the "Prophet of Truth," showered with fame and fortune. While investigating safety hazards in a new skyscraper, she habitually snaps a photo of the building. As the picture develops, she sees the tower engulfed in flames. Reflected in the fire is a cold, determined face pressing a detonator—her own. The date on the photo is one week away. She has no idea why she would commit such an act. Is it an extreme measure to expose a greater conspiracy? Is she being framed? Or will she, at some point in the future, simply break bad? The prophecy traps her in a paradox: if she does nothing, she becomes a mass murderer; if she tries to stop herself, how can she fight a plot orchestrated by her future self, a plot she currently knows nothing about?
                玛雅是一名渴望揭露真相却处处碰壁的小报记者，她偶然得到一部旧的宝丽来相机。她很快发现，这部相机拍出的不是当下，而是被拍摄对象或地点在未来最重要的一个“决定性瞬间”。她用它拍下市长贪腐的交易现场，提前曝光；她拍下即将崩盘的股票K线图，拯救了无数股民。她成了预言真相的“先知”，名利双收。在一次调查城市摩天楼的建筑安全隐患时，她习惯性地对着大楼拍了一张。照片显影后，她看到了熊熊燃烧的大楼，以及在火光映照下，一张按下引爆器的、冷酷的脸——那是她自己的脸。照片上的时间是一周后。她不明白自己为何会成为纵火犯。是为了揭露一个更大的阴谋而采取的极端手段？还是她将被某人陷害？或是在未来的某个节点，她会彻底黑化？这个预言让她陷入了悖论：如果她什么都不做，她将成为杀人犯；如果她试图阻止自己，又该如何对抗一个由未来“自己”布下的、她自己毫不知情的局？
                
                喜爱度：65%
                The Perfect Life Script 完美人生剧本
                概括：她发现一份精准预言自己一切的“人生剧本”，几次反抗都被所爱之人“矫正”，惊觉众人皆为演员；她删档时，未婚夫低语：现在可以重启了。
                Tag：#HighConcept #Mystery #ExistentialThriller
                Chloe’s life is flawless—a dream career, a perfect fiancé, a glittering future. Until she finds a digital file titled “Chloe_LifeScript_v3.” It predicts every event, every thought she’ll have—word for word. Terrified, she tests it, only to watch the script unfold exactly as written. Determined to defy it, she starts acting irrationally, destroying her routines. Yet each rebellion is quietly “corrected” by the people who love her most. The realization hits: they’re not real—they’re actors following her script. Panicked, Chloe deletes the file.
                Behind her, her fiancé exhales in relief and says softly, “Good. Now we can start over.”
                克洛伊的生活无可挑剔——梦想的职业、完美的未婚夫、光明的未来。直到她发现了一个名为"Chloe_LifeScript_v3"的数字文件。它预测了每一个事件,她将产生的每一个想法——一字不差。
                惊恐之下,她测试了这个剧本,却眼睁睁看着一切完全按照文件所写展开。决心反抗的她开始做出非理性的行为,破坏自己的日常习惯。然而每一次反叛都被最爱她的人"悄悄地"纠正了回来。
                真相击中了她:他们都不是真实的——他们是按照她的剧本演戏的演员。
                惊慌失措的克洛伊删除了文件。在她身后,未婚夫松了一口气,轻声说道:"很好。现在我们可以重新开始了。"
                
                喜爱度：65%
                The Midnight Oracle Hotline 午夜占卜热线
                概括：经营通灵热线的诺拉接到“梦中之声”，追查竟连到亡未婚夫的旧号；她跨越三年线警告事故，时间改写成她受伤、他还在，醒来见他含泪守候。
                Tag：#Urban Fantasy, Supernatural Romance, Fate
                In New York, Nora runs a "Midnight Oracle Hotline"—a fake psychic service for lonely night callers. She improvises mystical advice to comfort strangers. One night, a man calls saying, "I think you're the voice in my dreams."
                Intrigued, Nora keeps answering his calls, but the man describes her apartment, her cat, her past—things he couldn't possibly know. When she traces the number, it leads to a disconnected line registered under her deceased fiancé's name. As her dreams start syncing with his words, Nora realizes she's talking to a version of him that exists three years in the past—before the accident.
                She has one final call to make before the timeline closes: tell him not to drive that night.
                She warns him. The timeline shifts. She wakes up in a hospital—she was in the car that night instead. He's alive, and he never left. Three years of waiting, hoping, loving her through the silence. When she finally wakes, his face is the first thing she sees—and he's smiling through tears.
                在纽约,诺拉经营着一个"午夜神谕热线"——一个为孤独的深夜来电者提供的假通灵服务。她即兴编造神秘的建议来安慰陌生人。一天晚上,一个男人打来电话说:"我觉得你是我梦中的声音。"
                诺拉被吸引了,继续接听他的电话,但这个男人描述了她的公寓、她的猫、她的过去——他不可能知道的事情。当她追踪电话号码时,发现这是一个已停机的号码,登记在她已故未婚夫的名下。随着她的梦境开始与他的话同步,诺拉意识到她正在与三年前的他通话——在那场事故之前。
                在时间线关闭之前,她还有最后一通电话要打:告诉他那天晚上不要开车。
                她警告了他。时间线转变了。她在医院醒来——那天晚上在车里的是她。他还活着,他从未离开。三年的等待,希望,在沉默中爱着她。当她终于醒来时,她看到的第一张脸是他的——他含泪微笑着。
                
                喜爱度：65%
                The Dream Writer 梦境作者
                概括：作家艾玛在梦中与陌生人相恋，竟发现他是昏迷三月的消防员；她以温暖梦境为路标，把爱化作引导，带他从沉睡归来。
                Tag：# Mystery # Romance # Supernatural
                Novelist Emma, struggling with writer's block, begins meeting a charming stranger named Daniel in her dreams. They talk for hours in vivid dreamscapes—always lit by warm, golden firelight: cozy fireplaces, floating lanterns, fields of fireflies. Each morning she wakes and writes down everything, creating her best work yet. Night after night, she falls in love with him.
                Then Emma sees Daniel's face on the news: he's a firefighter who's been in a coma for three months. She visits the hospital and recognizes him. A doctor mentions coma patients sometimes create dream connections when they're trying to find their way back.
                Emma realizes: Daniel is trapped, and she's the only one who can guide him out.
                小说家艾玛正在与写作瓶颈作斗争,却开始在梦中遇见一位迷人的陌生人丹尼尔。他们在充满生机的梦境中交谈数小时——总是被温暖的金色火光照亮:舒适的壁炉、漂浮的灯笼、萤火虫的原野。每天早晨她醒来后将一切记录下来,创作出她最好的作品。一夜又一夜,她爱上了他。
                然后艾玛在新闻上看到了丹尼尔的脸:他是一名消防员,已经昏迷了三个月。她去医院探望并立刻认出了他。一位医生提到,昏迷病人有时会在试图寻找回来的路时创造梦境连接。
                艾玛意识到:丹尼尔被困住了,而她是唯一能引导他出来的人。

                待评估内容：\n{st.session_state['res']}
                """
                st.session_state['filtered_res'] = call_ai_engine(provider, api_key, model_name, filter_p)

with col_r:
    st.subheader("2. 创意输出展示")

    if 'filtered_res' in st.session_state:
        st.success("✅ 已为您筛选并展示前 5 名完整创意内容")
        # 增加高度以容纳 5 个完整创意
        st.text_area("筛选后的 Top 5 完整内容", st.session_state['filtered_res'], height=1000)
        st.divider()

    if 'res' in st.session_state:
        st.write("📋 原始生成的 30 个创意全量列表：")
        st.text_area("全量 30 个预览", st.session_state['res'], height=800)
    else:
        st.info("💡 请在左侧生成创意。")

st.markdown("---")
st.caption("ByteDance 内部专用 | 筛选结果已配置为完整内容展示")
