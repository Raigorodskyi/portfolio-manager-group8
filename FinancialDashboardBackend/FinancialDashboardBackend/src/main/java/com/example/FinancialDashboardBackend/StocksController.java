
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

@RestController
public class StocksController {

    @GetMapping("/api/top-performers")
    public ResponseEntity<String> getTopPerformers() throws IOException {
        ProcessBuilder pb = new ProcessBuilder("python3", "top_performers.py");
        pb.directory(new File("/path/to/your/script")); // Replace with the actual path to your script
        Process process = pb.start();

        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder output = new StringBuilder();
        String line;

        while ((line = reader.readLine()) != null) {
            output.append(line);
        }
        System.out.println(output);
        return ResponseEntity.ok(output.toString());
    }
}