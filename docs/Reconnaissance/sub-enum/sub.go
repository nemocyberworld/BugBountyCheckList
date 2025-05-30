package main

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)

func main() {
	// Ask for target domain
	fmt.Print("Enter your target domain: ")
	var domain string
	fmt.Scanln(&domain)

	inputFile := filepath.Join("results", domain, "amass.txt")
	outputFile := filepath.Join("results", domain, "extracted_subdomains.txt")

	fmt.Printf("[*] Starting subdomain extraction for domain: %s\n", domain)

	// Check if input file exists; if not, run amass
	if _, err := os.Stat(inputFile); os.IsNotExist(err) {
		fmt.Printf("[!] Input file not found: %s\n", inputFile)
		fmt.Println("[*] Running amass to enumerate subdomains...")

		// Make sure output directory exists
		if err := os.MkdirAll(filepath.Dir(inputFile), 0755); err != nil {
			fmt.Printf("[!] Could not create directory: %v\n", err)
			os.Exit(1)
		}

		// Run amass and save directly to file
		cmd := exec.Command("amass", "enum", "-passive", "-d", domain, "-o", inputFile)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr

		err := cmd.Run()
		if err != nil {
			fmt.Printf("[!] Failed to run amass: %v\n", err)
			os.Exit(1)
		}
		fmt.Println("[+] Amass enumeration complete.")

		// Check if amass output has content
		info, err := os.Stat(inputFile)
		if err != nil || info.Size() == 0 {
			fmt.Printf("[!] Amass did not find any subdomains for %s\n", domain)
			os.Exit(0)
		}
	} else {
		fmt.Printf("[*] Reading from: %s\n", inputFile)
	}

	// Open input file
	file, err := os.Open(inputFile)
	if err != nil {
		fmt.Printf("[!] Error opening file: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	// Count total lines first for progress estimation
	totalLines, err := lineCount(inputFile)
	if err != nil {
		fmt.Printf("[!] Error counting lines: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("[*] Total lines to process: %d\n", totalLines)

	startTime := time.Now()

	// Regex for valid subdomains: something.something.tld
	subdomainRegex := regexp.MustCompile(`^([a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$`)

	scanner := bufio.NewScanner(file)
	processed := 0
	subdomains := make(map[string]struct{})

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())

		if subdomainRegex.MatchString(line) {
			subdomains[line] = struct{}{}
		}

		processed++

		// Update progress every 100 lines or at the end
		if processed%100 == 0 || processed == totalLines {
			elapsed := time.Since(startTime)
			rate := float64(processed) / elapsed.Seconds()
			remaining := totalLines - processed

			var eta time.Duration
			if rate > 0 {
				eta = time.Duration(float64(remaining)/rate) * time.Second
			} else {
				eta = 0
			}

			fmt.Printf("\rProcessed: %d/%d lines | Elapsed: %s | ETA: %s        ",
				processed, totalLines,
				formatDuration(elapsed),
				formatDuration(eta),
			)
		}
	}
	fmt.Println() // Newline after progress

	if err := scanner.Err(); err != nil {
		fmt.Printf("[!] Error reading file: %v\n", err)
		os.Exit(1)
	}

	// Sort and write unique subdomains to output file
	fmt.Println("[*] Removing duplicates and sorting...")
	subsSlice := make([]string, 0, len(subdomains))
	for s := range subdomains {
		subsSlice = append(subsSlice, s)
	}
	sort.Strings(subsSlice)

	// Ensure output directory exists
	outDir := filepath.Dir(outputFile)
	if err := os.MkdirAll(outDir, 0755); err != nil {
		fmt.Printf("[!] Error creating output directory: %v\n", err)
		os.Exit(1)
	}

	out, err := os.Create(outputFile)
	if err != nil {
		fmt.Printf("[!] Error creating output file: %v\n", err)
		os.Exit(1)
	}
	defer out.Close()

	for _, sub := range subsSlice {
		fmt.Fprintln(out, sub)
	}

	totalTime := time.Since(startTime)
	fmt.Println("[+] Extraction complete!")
	fmt.Printf("[+] Output saved to: %s\n", outputFile)
	fmt.Printf("[+] Total time taken: %s\n", formatDuration(totalTime))
}

// lineCount counts the number of lines in a file
func lineCount(path string) (int, error) {
	f, err := os.Open(path)
	if err != nil {
		return 0, err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	count := 0
	for scanner.Scan() {
		count++
	}
	return count, scanner.Err()
}

// formatDuration formats duration as HH:mm:ss
func formatDuration(d time.Duration) string {
	h := int(d.Hours())
	m := int(d.Minutes()) % 60
	s := int(d.Seconds()) % 60
	return fmt.Sprintf("%02dh:%02dm:%02ds", h, m, s)
}
