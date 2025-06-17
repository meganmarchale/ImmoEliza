with open("all_links.txt", "r") as f:
    links = f.readlines()

unique_links = []

for link in links:
    link = link.strip()
    if link and link not in unique_links:
        unique_links.append(link)
        

with open("all_links_cleaned.txt", "w") as file:
    for link in unique_links:
        file.write(link + "\n")

print(f"File's cleaned: {len(unique_links)} unique links.")