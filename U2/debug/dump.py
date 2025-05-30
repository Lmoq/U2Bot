import uiautomator2 as u2, time
time.sleep(2)

d = u2.connect()
    
class types:
    click = "android.widget.TextView"
    text = "android.view.ViewGroup"

# Dump all TextView
selector = {"className": types.click }
for i in range(4):  # Arbitrary max limit
    el = d(**selector, instance=i)
    if not el.exists:
        break
    try:
        print(f"[Instance {i}] {el.info['className']} | {repr(el.info['text'])}")
    except Exception as e:
        print(f"TextWidget Instance {i}:Error")
        continue

# Dump all ViewGroup
selector = {"className": types.text }
for i in range(10,12):  # Arbitrary max limit
    el = d(**selector, instance=i)
    if not el.exists:
        break
    try:
        print(f"[Instance {i}] {el.info['className']} | {repr(el.info['text'])}")
        print(f"field : {el.selector}")
    except Exception as e:
        print(f"ViewGroup Instance {i}:Error")
        continue
