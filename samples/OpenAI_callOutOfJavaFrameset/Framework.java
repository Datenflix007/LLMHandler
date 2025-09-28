import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;

public class Framework {
    private ProcessBuilder processBuilder_doso;
    private Process process_doso;
    private String input;  

    Framework() {
        new MyFrame(this);  
    }

    public String[] runProcess(String str) {
        input = str;
        StringBuilder output = new StringBuilder();
        
        try {
            if (input == null || input.isEmpty()) {
                input = "Default input";  
            }

            
            processBuilder_doso = new ProcessBuilder("python", "openaiCaller.py", str);  
            processBuilder_doso.redirectErrorStream(true);

            Process process = processBuilder_doso.start();
            try (OutputStream os = process.getOutputStream()) {
                os.write(input.getBytes("UTF-8")); 
            }

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"));
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

       
        return new String[] {output.toString()};
    }

    public static void main(String[] args) {
        new Framework();  
    }
}

class MyFrame {

    private static ArrayList<String[]> chatHistory = new ArrayList<>();
    private JTextArea textArea;
    private JEditorPane chatHistoryArea;
    private Framework framework;
    private JScrollPane textAreaScrollPane;
    private JPanel textAreaPanel;
    private int initialHeight = 20;  

    MyFrame(Framework framework) {
        this.framework = framework; 
        
        // Erstelle das JFrame
        JFrame frame = new JFrame("Mein KI-Knecht");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(600, 600);  

        // Erstelle Panel für Layout
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));

        // Textarea für den Chatverlauf (JEditorPane für HTML-Inhalte)
        chatHistoryArea = new JEditorPane();
        chatHistoryArea.setEditable(false);
        chatHistoryArea.setContentType("text/html");  
        chatHistoryArea.setFont(new java.awt.Font("Arial", java.awt.Font.PLAIN, 14));

        // UTF-8 setzen
        chatHistoryArea.setText(""); 
        JScrollPane chatScrollPane = new JScrollPane(chatHistoryArea);
        chatScrollPane.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS);
        panel.add(chatScrollPane);

        textArea = new JTextArea(3, 20);
        textArea.setWrapStyleWord(true);
        textArea.setLineWrap(true);
        textArea.setText("Gib hier deinen Text ein.");
       
        textAreaPanel = new JPanel();
        textAreaPanel.setLayout(new BoxLayout(textAreaPanel, BoxLayout.Y_AXIS));
        
        textArea.setPreferredSize(new Dimension(150, initialHeight));
        textArea.setMinimumSize(new Dimension(100, initialHeight));
        textArea.setMaximumSize(new Dimension(150, Integer.MAX_VALUE));

        textAreaScrollPane = new JScrollPane(textArea);
        textAreaScrollPane.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS);
        
        textAreaPanel.add(textAreaScrollPane);
        panel.add(textAreaPanel);

        JButton button = new JButton("Absenden");
        button.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(Box.createRigidArea(new Dimension(0, 10)));
        panel.add(button);

        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                sendQuestion();
            }
        });

        textArea.addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                if (e.isControlDown() && e.getKeyCode() == KeyEvent.VK_ENTER) {
                    sendQuestion();
                }
            }
        });

        textAreaScrollPane.addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                initialHeight = textAreaScrollPane.getHeight();
            }
        });

        textAreaScrollPane.addMouseMotionListener(new MouseMotionAdapter() {
            public void mouseDragged(MouseEvent e) {
                int deltaY = e.getY() - initialHeight;
                if (deltaY > 0) {
                    int newHeight = Math.max(50, textAreaPanel.getHeight() + deltaY);
                    textAreaPanel.setPreferredSize(new Dimension(300, newHeight));
                    textAreaScrollPane.revalidate();
                    textAreaPanel.repaint();
                }
            }
        });

        frame.add(panel);
        frame.setVisible(true);
    }

    private void sendQuestion() {
        String question = textArea.getText();

        if (!question.isEmpty()) {
            String timeStamp = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm"));
            chatHistory.add(new String[] {timeStamp + " >>> " + question, ""});
            textArea.setText("");
            updateChatHistory();
            String[] response = framework.runProcess(question); 
            setAnswer(response);
        }
    }

    private void setAnswer(String[] response) {
        if (!chatHistory.isEmpty()) {
            int lastIndex = chatHistory.size() - 1;
            chatHistory.get(lastIndex)[1] = response[0];
            updateChatHistory();
        }
    }

    private void updateChatHistory() {
        StringBuilder chatContent = new StringBuilder();

        for (String[] chatEntry : chatHistory) {
            chatContent.append("<div style='border-radius: 15px; background-color: #d1e7ff; padding: 5px; margin: 5px 0; width: 80%; float: left; text-align: justify;'>")
                .append("<strong>Frage: </strong>").append(chatEntry[0]).append("</div>");

            chatContent.append("<div style='border-radius: 15px; background-color: #f7f7f7; padding: 5px; margin: 5px 0; width: 80%; float: right; text-align: justify; margin-left: 20%;'>")
                .append("<strong>Antwort: </strong>").append(chatEntry[1]).append("</div><br style='clear: both;'>");
        }

        chatHistoryArea.setText("<html>" + chatContent.toString() + "</html>");
    }
}
