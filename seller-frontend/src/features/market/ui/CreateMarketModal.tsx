import {
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  Button,
} from "@mui/material";
import { useState } from "react";
import { useCreateMarketMutation } from "../../../entities/market/api/marketApi";

interface Props {
  open: boolean;
  onSuccess: () => void;
}

export const CreateMarketModal = ({ open, onSuccess }: Props) => {
  const [name, setName] = useState("");
  const [createMarket, { isLoading }] = useCreateMarketMutation();

  const handleSubmit = async () => {
    if (!name.trim()) return;

    try {
      await createMarket({ marketName: name }).unwrap();
      onSuccess();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Dialog open={open} disableEscapeKeyDown>
      <DialogTitle color="#000000">Создание магазина</DialogTitle>

      <DialogContent>
        <TextField
          fullWidth
          label="Название магазина"
          value={name}
          onChange={(e) => setName(e.target.value)}
          margin="normal"
        />

        <Button
          variant="contained"
          fullWidth
          onClick={handleSubmit}
          disabled={isLoading}
        >
          Подтвердить
        </Button>
      </DialogContent>
    </Dialog>
  );
};
