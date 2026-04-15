import { type ReactNode, useState, useEffect } from "react";
import { Box } from "@mui/material";
import styles from "./MainLayout.module.css";
import { Header } from "../../widgets/header/ui/Header";
import { Footer } from "../../widgets/footer/ui/Footer";
import { useGetMyMarketQuery } from "../../entities/market/api/marketApi";
import { CreateMarketModal } from "../../features/market/ui/CreateMarketModal";

interface Props {
  children: ReactNode;
}

export const MainLayout = ({ children }: Props) => {
  const { data, error, refetch } = useGetMyMarketQuery(undefined);
  const userName = data?.marketName;

  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if ((error as any)?.status === 404) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setModalOpen(true);
    }
  }, [error]);

  const handleSuccess = async () => {
    setModalOpen(false);
    await refetch();
  };

  return (
    <Box className={styles.background}>
      <Box className={styles.container}>
        <Header userName={userName} />

        <Box sx={{ flex: 1 }}>{children}</Box>

        <Footer />

        <CreateMarketModal open={modalOpen} onSuccess={handleSuccess} />
      </Box>
    </Box>
  );
};
