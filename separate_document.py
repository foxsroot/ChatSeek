import re

file_name = {"comp.graphics.txt", "comp.os.ms-windows.misc.txt", "comp.sys.ibm.pc.hardware.txt", "comp.sys.mac.hardware.txt", "comp.windows.x.txt", "misc.forsale.txt", "rec.autos.txt", "rec.motorcycles.txt", "rec.sport.baseball.txt", "rec.sport.hockey.txt", "sci.crypt.txt", "sci.electronics.txt", "sci.med.txt", "sci.med.txt", "sci.space.txt", "soc.religion.christian.txt", "talk.politics.guns.txt", "talk.politics.mideast.txt", "talk.religion.misc.txt", "talk.politics.misc.txt"}

for everything in file_name:
    pattern = re.compile(r"(Newsgroup: .+?\n)(document_id: (\d+)\n)(From: .+?\n)(Subject: .+?\n)(.*?)(?=Newsgroup: |$)",
                         re.DOTALL)

    with open('documents/' + everything, 'r', encoding='ISO-8859-1') as file:
        content = file.read()

    matches = pattern.findall(content)

    for match in matches:
        newsgroup = match[0]
        document_id = match[2]
        from_field = match[3]
        subject = match[4]
        body = match[5]

        document_content = f"{newsgroup}{match[1]}{from_field}{subject}{body}"

        with open(f"documents_separated/{document_id}.txt", 'w', encoding='utf-8') as doc_file:
            doc_file.write(document_content)

print("Documents separated and saved successfully!")
